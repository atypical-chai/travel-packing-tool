"""Deploy / update the travel-packing-tool AWS pilot stack.

Steps this script can run:
  1) create/update CloudFormation stack
  2) package + upload Lambda code
  3) sync frontend to S3 and invalidate CloudFront
  4) set CORS to include the CloudFront origin
  5) write aws-pilot/staging-outputs.json for handoff docs
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from build_lambda import main as build_lambda

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "infra" / "template.yaml"
OUTPUTS = ROOT / "aws-pilot" / "staging-outputs.json"
FRONTEND = ROOT / "frontend"
STACK_NAME = "travel-packing-tool-staging"
REGION = "us-west-2"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def aws_json(cmd: list[str]):
    result = run(cmd)
    if result.stderr:
        print(result.stderr)
    return json.loads(result.stdout) if result.stdout.strip() else {}


def stack_exists() -> bool:
    result = run(
        [
            "aws",
            "cloudformation",
            "describe-stacks",
            "--stack-name",
            STACK_NAME,
            "--region",
            REGION,
        ],
        check=False,
    )
    return result.returncode == 0


def wait_stack(action: str) -> None:
    waiter = "stack-create-complete" if action == "create" else "stack-update-complete"
    run(
        [
            "aws",
            "cloudformation",
            "wait",
            waiter,
            "--stack-name",
            STACK_NAME,
            "--region",
            REGION,
        ]
    )


def deploy_stack(cors_origins: str, budget_email: str) -> None:
    # Copy template to a space-free temp path — AWS CLI on Windows mishandles
    # file:// URIs that contain spaces or Z: mapped drives.
    import tempfile
    import shutil

    tmp_dir = Path(tempfile.gettempdir()) / "travel-packing-tool-cfn"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_template = tmp_dir / "template.yaml"
    shutil.copy2(TEMPLATE, tmp_template)
    template_path = str(tmp_template)

    param_path = tmp_dir / "params.json"
    param_path.write_text(
        json.dumps(
            [
                {"ParameterKey": "EnvironmentName", "ParameterValue": "staging"},
                {"ParameterKey": "CorsOrigins", "ParameterValue": cors_origins},
                {"ParameterKey": "BudgetEmail", "ParameterValue": budget_email},
            ]
        ),
        encoding="utf-8",
    )

    # `deploy` accepts a normal filesystem path and creates/updates safely.
    cmd = [
        "aws",
        "cloudformation",
        "deploy",
        "--stack-name",
        STACK_NAME,
        "--template-file",
        template_path,
        "--parameter-overrides",
        f"EnvironmentName=staging",
        f"CorsOrigins={cors_origins}",
        f"BudgetEmail={budget_email}",
        "--capabilities",
        "CAPABILITY_NAMED_IAM",
        "--region",
        REGION,
    ]
    result = run(cmd, check=False)
    out = (result.stdout or "") + (result.stderr or "")
    print(out)
    if result.returncode != 0:
        if "No changes to deploy" in out or "No updates are to be performed" in out:
            print("Stack already up to date")
            return
        raise SystemExit("Stack deploy failed")


def get_outputs() -> dict:
    data = aws_json(
        [
            "aws",
            "cloudformation",
            "describe-stacks",
            "--stack-name",
            STACK_NAME,
            "--region",
            REGION,
            "--query",
            "Stacks[0].Outputs",
            "--output",
            "json",
        ]
    )
    return {item["OutputKey"]: item["OutputValue"] for item in data}


def update_lambda_code(function_name: str) -> str:
    zip_path = build_lambda()
    result = aws_json(
        [
            "aws",
            "lambda",
            "update-function-code",
            "--function-name",
            function_name,
            "--zip-file",
            f"fileb://{zip_path.as_posix()}",
            "--region",
            REGION,
        ]
    )
    # Wait until update finishes before changing config.
    run(
        [
            "aws",
            "lambda",
            "wait",
            "function-updated",
            "--function-name",
            function_name,
            "--region",
            REGION,
        ]
    )
    return result.get("Version", "$LATEST")


def publish_lambda_version(function_name: str, description: str) -> str:
    data = aws_json(
        [
            "aws",
            "lambda",
            "publish-version",
            "--function-name",
            function_name,
            "--description",
            description,
            "--region",
            REGION,
        ]
    )
    return str(data["Version"])


def sync_frontend(bucket: str, api_base_url: str, distribution_id: str) -> None:
    # Write environment-specific config into a temp copy under infra/.build/frontend
    stage = ROOT / "infra" / ".build" / "frontend"
    stage.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "styles.css", "script.js"):
        (stage / name).write_bytes((FRONTEND / name).read_bytes())
    (stage / "config.js").write_text(
        f"window.TRAVEL_PACKING_API_BASE_URL = '{api_base_url.rstrip('/')}';\n",
        encoding="utf-8",
    )
    # Versioned-ish cache: HTML short, assets longer.
    run(
        [
            "aws",
            "s3",
            "sync",
            str(stage),
            f"s3://{bucket}/",
            "--delete",
            "--region",
            REGION,
            "--cache-control",
            "max-age=60",
        ]
    )
    run(
        [
            "aws",
            "cloudfront",
            "create-invalidation",
            "--distribution-id",
            distribution_id,
            "--paths",
            "/*",
            "--region",
            REGION,
        ]
    )


def save_outputs(outputs: dict, extra: dict | None = None) -> None:
    payload = dict(outputs)
    if extra:
        payload.update(extra)
    OUTPUTS.parent.mkdir(parents=True, exist_ok=True)
    OUTPUTS.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Wrote", OUTPUTS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase",
        choices=["infra", "frontend-render", "backend", "frontend-aws-api", "all"],
        default="all",
    )
    parser.add_argument("--budget-email", default="ambujsriv@gmail.com")
    args = parser.parse_args()

    base_cors = ",".join(
        [
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "https://travel-packing-tool.vercel.app",
        ]
    )

    if args.phase in {"infra", "all"}:
        deploy_stack(base_cors, args.budget_email)

    outputs = get_outputs()
    cf_url = outputs["CloudFrontUrl"]
    cors = base_cors + "," + cf_url

    if args.phase in {"infra", "all", "backend"}:
        # Refresh stack CORS with CloudFront origin, then upload real Lambda code.
        deploy_stack(cors, args.budget_email)
        outputs = get_outputs()
        version = update_lambda_code(outputs["ApiFunctionName"])
        published = publish_lambda_version(
            outputs["ApiFunctionName"], f"pilot-{int(time.time())}"
        )
        save_outputs(outputs, {"LambdaCodeVersion": published, "CorsOrigins": cors})

    outputs = get_outputs()
    if args.phase in {"frontend-render", "all"}:
        sync_frontend(
            outputs["FrontendBucketName"],
            "https://travel-packing-tool-backend.onrender.com",
            outputs["CloudFrontDistributionId"],
        )
        save_outputs(
            outputs,
            {
                "FrontendApiTarget": "render",
                "FrontendApiBaseUrl": "https://travel-packing-tool-backend.onrender.com",
                "CorsOrigins": cors,
            },
        )

    if args.phase in {"frontend-aws-api", "all"}:
        sync_frontend(
            outputs["FrontendBucketName"],
            outputs["ApiEndpoint"],
            outputs["CloudFrontDistributionId"],
        )
        save_outputs(
            outputs,
            {
                "FrontendApiTarget": "aws",
                "FrontendApiBaseUrl": outputs["ApiEndpoint"],
                "CorsOrigins": cors,
            },
        )

    print(json.dumps(get_outputs(), indent=2))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(exc.stdout)
        print(exc.stderr)
        sys.exit(exc.returncode)
