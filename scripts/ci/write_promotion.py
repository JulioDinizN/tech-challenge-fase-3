#!/usr/bin/env python3
"""Create one non-secret image promotion descriptor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG = REPO_ROOT / ".ci" / "services.json"
IMAGE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._/-]+$")
TAG_PATTERN = re.compile(r"^sha-[0-9a-f]{12}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    allowed = {entry["name"] for entry in catalog}
    if args.service not in allowed:
        raise ValueError(f"unknown service: {args.service}")
    if not IMAGE_PATTERN.fullmatch(args.image):
        raise ValueError("image path is invalid")
    if not TAG_PATTERN.fullmatch(args.tag):
        raise ValueError("image tag must use sha-<12 lowercase hex characters>")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {"service": args.service, "image": args.image, "tag": args.tag},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
