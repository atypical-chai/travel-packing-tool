"""Build a Lambda deployment zip for the Travel Packing Tool API.

Why: packages FastAPI + Mangum + the read-only SQLite catalog into one zip
that `aws lambda update-function-code` can upload. No SAM CLI required.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
BUILD = ROOT / "infra" / ".build"
STAGE = BUILD / "lambda"
ZIP_PATH = BUILD / "api.zip"


def main() -> Path:
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True, exist_ok=True)

    # Install Linux-compatible deps when possible; fall back to local wheels.
    # Lambda runs Amazon Linux; on Windows we still install pure-Python packages.
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(BACKEND / "requirements.txt"),
        "-t",
        str(STAGE),
        "--upgrade",
        "--quiet",
    ]
    # Prefer manylinux wheels so pydantic/fastapi binaries match Lambda.
    cmd.extend(["--platform", "manylinux2014_x86_64", "--implementation", "cp", "--python-version", "3.13", "--only-binary=:all:"])
    print("Installing dependencies into", STAGE)
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print("manylinux-only install failed; retrying without platform pins")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(BACKEND / "requirements.txt"),
                "-t",
                str(STAGE),
                "--upgrade",
                "--quiet",
            ],
            check=True,
        )

    # Copy application modules + catalog (never run seed).
    for name in (
        "main.py",
        "models.py",
        "list_generator.py",
        "database.py",
        "items_data.py",
    ):
        src = BACKEND / name
        if src.exists():
            shutil.copy2(src, STAGE / name)

    db_src = BACKEND / "database" / "items.db"
    db_dst = STAGE / "database"
    db_dst.mkdir(exist_ok=True)
    shutil.copy2(db_src, db_dst / "items.db")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in STAGE.rglob("*"):
            if path.is_file():
                # Skip bytecode caches
                if "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                zf.write(path, path.relative_to(STAGE).as_posix())

    size_mb = ZIP_PATH.stat().st_size / (1024 * 1024)
    print(f"Wrote {ZIP_PATH} ({size_mb:.2f} MB)")
    return ZIP_PATH


if __name__ == "__main__":
    main()
