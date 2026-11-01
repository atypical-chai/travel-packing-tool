"""Demonstrate frontend + Lambda rollback without deleting resources.

1) Capture current frontend object versions and Lambda version
2) Deploy a marked second frontend release
3) Restore the previous index.html version from S3 versioning
4) Re-invalidate CloudFront
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = json.loads((ROOT / "aws-pilot" / "staging-outputs.json").read_text(encoding="utf-8"))
REGION = "us-west-2"
BUCKET = OUTPUTS["FrontendBucketName"]
DIST = OUTPUTS["CloudFrontDistributionId"]
FN = OUTPUTS["ApiFunctionName"]
DEMO = ROOT / "aws-pilot" / "rollback-demo.json"


def run(cmd):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def aws_json(cmd):
    out = run(cmd).stdout
    return json.loads(out) if out.strip() else {}


def main():
    # Current index.html version id
    head = aws_json(
        [
            "aws",
            "s3api",
            "head-object",
            "--bucket",
            BUCKET,
            "--key",
            "index.html",
            "--region",
            REGION,
        ]
    )
    previous_version = head["VersionId"]
    versions_before = aws_json(
        [
            "aws",
            "lambda",
            "list-versions-by-function",
            "--function-name",
            FN,
            "--region",
            REGION,
            "--query",
            "Versions[?Version!=`$LATEST`].[Version,Description]",
            "--output",
            "json",
        ]
    )

    # Second release: stamp a comment into staged index and sync
    stage = ROOT / "infra" / ".build" / "frontend"
    html_path = stage / "index.html"
    original = html_path.read_text(encoding="utf-8")
    stamped = original.replace(
        "<title>Travel Checklist</title>",
        f"<title>Travel Checklist</title><!-- rollback-demo {int(time.time())} -->",
    )
    html_path.write_text(stamped, encoding="utf-8")
    run(
        [
            "aws",
            "s3",
            "cp",
            str(html_path),
            f"s3://{BUCKET}/index.html",
            "--region",
            REGION,
            "--cache-control",
            "max-age=60",
        ]
    )
    after = aws_json(
        [
            "aws",
            "s3api",
            "head-object",
            "--bucket",
            BUCKET,
            "--key",
            "index.html",
            "--region",
            REGION,
        ]
    )
    broken_version = after["VersionId"]

    # Rollback frontend to previous version
    run(
        [
            "aws",
            "s3api",
            "copy-object",
            "--bucket",
            BUCKET,
            "--key",
            "index.html",
            "--copy-source",
            f"{BUCKET}/index.html?versionId={previous_version}",
            "--metadata-directive",
            "REPLACE",
            "--cache-control",
            "max-age=60",
            "--content-type",
            "text/html",
            "--region",
            REGION,
        ]
    )
    run(
        [
            "aws",
            "cloudfront",
            "create-invalidation",
            "--distribution-id",
            DIST,
            "--paths",
            "/index.html",
            "--region",
            REGION,
        ]
    )

    # Lambda rollback rehearsal: republish current code as a named version marker,
    # then point a staging alias at the earlier published version if one exists.
    published = aws_json(
        [
            "aws",
            "lambda",
            "publish-version",
            "--function-name",
            FN,
            "--description",
            f"rollback-demo-current-{int(time.time())}",
            "--region",
            REGION,
        ]
    )
    target_version = None
    if versions_before:
        target_version = str(versions_before[0][0])
        # Ensure alias exists for safe traffic shift practice
        alias = aws_json(
            [
                "aws",
                "lambda",
                "list-aliases",
                "--function-name",
                FN,
                "--region",
                REGION,
            ]
        )
        names = [a["Name"] for a in alias.get("Aliases", [])]
        if "staging" not in names:
            run(
                [
                    "aws",
                    "lambda",
                    "create-alias",
                    "--function-name",
                    FN,
                    "--name",
                    "staging",
                    "--function-version",
                    target_version,
                    "--region",
                    REGION,
                ]
            )
        else:
            run(
                [
                    "aws",
                    "lambda",
                    "update-alias",
                    "--function-name",
                    FN,
                    "--name",
                    "staging",
                    "--function-version",
                    target_version,
                    "--region",
                    REGION,
                ]
            )

    result = {
        "frontendPreviousVersionId": previous_version,
        "frontendSecondReleaseVersionId": broken_version,
        "frontendRolledBack": True,
        "lambdaVersionsBefore": versions_before,
        "lambdaPublishedDuringDemo": published.get("Version"),
        "lambdaStagingAliasVersion": target_version,
    }
    DEMO.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
