"""Compare a candidate API against saved Render baseline fixtures."""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "aws-pilot" / "baseline"

CASES = {
    "vacation_domestic": {
        "destination": "Paris",
        "tripType": "general",
        "weather": [],
        "gear": [],
        "activities": [],
        "tripScope": "domestic",
    },
    "work_international": {
        "destination": "Berlin",
        "tripType": "work",
        "weather": ["hot"],
        "gear": ["laptop"],
        "activities": [],
        "tripScope": "international",
    },
    "outdoor_cold_rain": {
        "destination": "Alaska",
        "tripType": "outdoor",
        "weather": ["cold", "rain"],
        "gear": [],
        "activities": ["fitness"],
        "tripScope": "domestic",
    },
}


def call(base: str, method: str, path: str, body=None):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base.rstrip("/") + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


def normalize_checklist(payload: dict) -> dict:
    return {
        key: sorted([item["text"] for item in payload.get(key, [])])
        for key in ("pack", "buy", "do")
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()

    failures = 0
    status, body = call(args.base_url, "GET", "/")
    print("GET /", status, body)
    if status != 200:
        failures += 1

    status, body = call(args.base_url, "GET", "/api/form-options")
    print("GET /api/form-options", status)
    if status != 200:
        failures += 1

    for name, payload in CASES.items():
        expected = json.loads((BASELINE / f"{name}.json").read_text(encoding="utf-8"))["body"]
        status, actual = call(args.base_url, "POST", "/api/generate-checklist", payload)
        exp_n = normalize_checklist(expected)
        act_n = normalize_checklist(actual if isinstance(actual, dict) else {})
        ok = status == 200 and exp_n == act_n
        print(name, "OK" if ok else "FAIL", status, {k: len(act_n[k]) for k in act_n})
        if not ok:
            failures += 1
            print(" expected", exp_n)
            print(" actual  ", act_n)

    # Invalid / incomplete body should be 422 (not silently falling back)
    status, _ = call(args.base_url, "POST", "/api/generate-checklist", {"destination": ""})
    print("invalid body", status)
    if status != 422:
        failures += 1

    print("failures", failures)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
