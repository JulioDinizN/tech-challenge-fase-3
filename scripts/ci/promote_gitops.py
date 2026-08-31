#!/usr/bin/env python3
"""Apply a set of image descriptors to one GitOps checkout atomically."""

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
    parser.add_argument("--gitops-root", required=True, type=Path)
    parser.add_argument("--promotions", required=True, type=Path)
    return parser.parse_args()


def load_promotions(directory: Path, allowed: set[str]) -> dict[str, dict[str, str]]:
    promotions: dict[str, dict[str, str]] = {}
    for path in sorted(directory.rglob("*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        service = item.get("service", "")
        image = item.get("image", "")
        tag = item.get("tag", "")
        if service not in allowed:
            raise ValueError(f"{path}: unknown service {service!r}")
        if not IMAGE_PATTERN.fullmatch(image):
            raise ValueError(f"{path}: invalid image path")
        if not TAG_PATTERN.fullmatch(tag):
            raise ValueError(f"{path}: invalid immutable tag")
        normalized = {"service": service, "image": image, "tag": tag}
        if service in promotions and promotions[service] != normalized:
            raise ValueError(f"conflicting promotions for {service}")
        promotions[service] = normalized
    if not promotions:
        raise ValueError("no promotion descriptors were found")
    return promotions


def update_kustomization(path: Path, promotion: dict[str, str]) -> None:
    service = promotion["service"]
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(?m)(^\s*- name: togglemaster/{re.escape(service)}\s*$"
        rf"\n^\s+newName: ).*$"
        rf"\n(^\s+newTag: ).*$"
    )
    replacement = rf"\g<1>{promotion['image']}\n\g<2>{promotion['tag']}"
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise ValueError(
            f"could not find exactly one image block for {service} in {path}"
        )
    path.write_text(updated, encoding="utf-8")


def main() -> int:
    args = parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    allowed = {entry["name"] for entry in catalog}
    promotions = load_promotions(args.promotions, allowed)

    for service, promotion in sorted(promotions.items()):
        target = (
            args.gitops_root
            / "apps"
            / service
            / "overlays"
            / "homolog"
            / "kustomization.yaml"
        )
        if not target.is_file():
            raise ValueError(f"GitOps target does not exist: {target}")
        update_kustomization(target, promotion)
        print(f"promoted {service} to {promotion['tag']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
