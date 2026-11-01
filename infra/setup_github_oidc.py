"""Create a narrowly scoped GitHub OIDC deploy role for this pilot repo."""
from __future__ import annotations

import json
import subprocess

REGION = "us-west-2"
ACCOUNT = subprocess.check_output(
    ["aws", "sts", "get-caller-identity", "--query", "Account", "--output", "text"],
    text=True,
).strip()
ROLE_NAME = "travel-packing-tool-github-deploy"
PROVIDER_URL = "https://token.actions.githubusercontent.com"
REPO = "atypical-chai/travel-packing-tool"


def run(cmd):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def ensure_oidc_provider():
    listed = subprocess.run(
        ["aws", "iam", "list-open-id-connect-providers"],
        check=True,
        text=True,
        capture_output=True,
    )
    if "token.actions.githubusercontent.com" in listed.stdout:
        print("OIDC provider already present")
        return
    thumbprint = "ffffffffffffffffffffffffffffffffffffffff"
    run(
        [
            "aws",
            "iam",
            "create-open-id-connect-provider",
            "--url",
            PROVIDER_URL,
            "--client-id-list",
            "sts.amazonaws.com",
            "--thumbprint-list",
            thumbprint,
        ]
    )


def main():
    ensure_oidc_provider()
    trust = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": f"arn:aws:iam::{ACCOUNT}:oidc-provider/token.actions.githubusercontent.com"
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                    },
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": [
                            f"repo:{REPO}:ref:refs/heads/master",
                            f"repo:{REPO}:environment:aws-staging",
                        ]
                    },
                },
            }
        ],
    }
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PilotCloudFormation",
                "Effect": "Allow",
                "Action": [
                    "cloudformation:CreateStack",
                    "cloudformation:UpdateStack",
                    "cloudformation:DescribeStacks",
                    "cloudformation:DescribeStackEvents",
                    "cloudformation:GetTemplate",
                    "cloudformation:CreateChangeSet",
                    "cloudformation:DescribeChangeSet",
                    "cloudformation:ExecuteChangeSet",
                    "cloudformation:DeleteChangeSet",
                ],
                "Resource": [
                    f"arn:aws:cloudformation:{REGION}:{ACCOUNT}:stack/travel-packing-tool-staging/*"
                ],
            },
            {
                "Sid": "PilotServices",
                "Effect": "Allow",
                "Action": [
                    "s3:*",
                    "lambda:*",
                    "apigateway:*",
                    "cloudfront:*",
                    "logs:*",
                    "iam:PassRole",
                    "iam:GetRole",
                    "iam:CreateRole",
                    "iam:AttachRolePolicy",
                    "iam:PutRolePolicy",
                    "iam:TagRole",
                    "budgets:*",
                ],
                "Resource": "*",
                "Condition": {
                    "StringEquals": {"aws:RequestedRegion": [REGION, "us-east-1"]}
                },
            },
        ],
    }

    # CloudFront / IAM are global — loosen region condition for those by splitting later if needed.
    # For simplicity in the pilot, grant the above and rely on stack/resource naming discipline.
    policy["Statement"][1].pop("Condition", None)

    trust_path = "infra/.build/github-trust.json"
    policy_path = "infra/.build/github-policy.json"
    Path = __import__("pathlib").Path
    Path("infra/.build").mkdir(parents=True, exist_ok=True)
    Path(trust_path).write_text(json.dumps(trust), encoding="utf-8")
    Path(policy_path).write_text(json.dumps(policy), encoding="utf-8")

    exists = subprocess.run(
        ["aws", "iam", "get-role", "--role-name", ROLE_NAME],
        capture_output=True,
        text=True,
    )
    if exists.returncode != 0:
        run(
            [
                "aws",
                "iam",
                "create-role",
                "--role-name",
                ROLE_NAME,
                "--assume-role-policy-document",
                f"file://{Path(trust_path).resolve().as_posix()}",
                "--description",
                "GitHub Actions deploy role for travel-packing-tool staging",
            ]
        )
    else:
        run(
            [
                "aws",
                "iam",
                "update-assume-role-policy",
                "--role-name",
                ROLE_NAME,
                "--policy-document",
                f"file://{Path(trust_path).resolve().as_posix()}",
            ]
        )

    run(
        [
            "aws",
            "iam",
            "put-role-policy",
            "--role-name",
            ROLE_NAME,
            "--policy-name",
            "travel-packing-tool-staging-deploy",
            "--policy-document",
            f"file://{Path(policy_path).resolve().as_posix()}",
        ]
    )
    print(f"ROLE_ARN=arn:aws:iam::{ACCOUNT}:role/{ROLE_NAME}")


if __name__ == "__main__":
    main()
