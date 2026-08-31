#!/usr/bin/env python3
"""Build a GitHub Actions matrix containing only changed services."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = REPO_ROOT / ".ci" / "services.json"
ZERO_SHA = "0" * 40
SHARED_PREFIXES = (
    ".ci/",
    ".github/workflows/_service-ci.yml",
    ".github/workflows/services-ci.yml",
    "docker/",
    "scripts/ci/",
)
SHARED_FILES = {"docker-compose.yml"}


def run_git(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def load_catalog(path: Path) -> list[dict[str, str]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, list) or not document:
        raise ValueError("service catalog must be a non-empty JSON array")

    required = {"name", "path", "language", "runtime_version"}
    for service in document:
        missing = required.difference(service)
        if missing:
            raise ValueError(
                f"service catalog entry is missing: {', '.join(sorted(missing))}"
            )
    return document


def revision_exists(revision: str) -> bool:
    if not revision or revision == ZERO_SHA:
        return False
    return run_git("cat-file", "-e", f"{revision}^{{commit}}").returncode == 0


def changed_files(base: str, head: str) -> list[str] | None:
    if not revision_exists(base) or not revision_exists(head):
        return None
    result = run_git("diff", "--name-only", "--diff-filter=ACMR", base, head)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return [line for line in result.stdout.splitlines() if line]


def select_services(
    catalog: list[dict[str, str]], files: list[str] | None
) -> list[dict[str, str]]:
    if files is None:
        return catalog

    shared_change = any(
        file in SHARED_FILES or file.startswith(SHARED_PREFIXES) for file in files
    )
    if shared_change:
        return catalog

    selected = []
    for service in catalog:
        prefix = service["path"].rstrip("/") + "/"
        if any(file.startswith(prefix) for file in files):
            selected.append(service)
    return selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog = load_catalog(args.catalog)
    files = changed_files(args.base, args.head)
    selected = select_services(catalog, files)
    print(json.dumps({"include": selected}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
