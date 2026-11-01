"""Smoke-check the CloudFront frontend HTML/JS and config API target."""
from __future__ import annotations

import argparse
import re
import sys
import urllib.request


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as resp:
        if resp.status != 200:
            raise SystemExit(f"{url} -> {resp.status}")
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--expect-api", required=True, help="Substring expected in config.js")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    html = fetch(base + "/")
    for needle in ("script.js", "styles.css", "config.js", "tripForm"):
        if needle not in html:
            print("FAIL missing", needle)
            return 1

    config = fetch(base + "/config.js")
    if args.expect_api.rstrip("/") not in config:
        print("FAIL config.js API mismatch")
        print(config)
        return 1

    js = fetch(base + "/script.js")
    if "resolveApiBaseUrl" not in js:
        print("FAIL script.js missing resolveApiBaseUrl")
        return 1

    # Guardrail: page must not hardcode only the fallback list without API path.
    if "generate-checklist" not in js:
        print("FAIL script.js missing generate-checklist call")
        return 1

    print("frontend smoke OK", base)
    print("config:", re.sub(r"\s+", " ", config).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
