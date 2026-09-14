#!/usr/bin/env bash
set -euo pipefail

required=(docker helm jq kubectl oci python3 terraform)
missing=()

for command in "${required[@]}"; do
  if command -v "$command" >/dev/null; then
    printf '%-12s %s\n' "$command" "$(command -v "$command")"
  else
    printf '%-12s MISSING\n' "$command"
    missing+=("$command")
  fi
done

if ((${#missing[@]})); then
  echo "Install the missing commands before the OCI deployment window: ${missing[*]}" >&2
  exit 1
fi

echo "Cloud deployment prerequisites are available."
