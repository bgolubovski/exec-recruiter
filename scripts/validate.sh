#!/usr/bin/env bash
# Validate plugin.json and marketplace.json against the local Claude Code
# version's schema. Run before every commit that touches .claude-plugin/.
#
# Why: CC v2.1.x has a stricter offline validator than the schemas published
# in claude-plugins-official. Object-form source types ({source: "url"|
# "github"|"git-subdir"}) fail in v2.1.x even though they appear in the
# canonical marketplace. The only working source for whole-repo plugins is
# the string "./" (with trailing slash — "." alone fails).
#
# Usage: ./scripts/validate.sh
# Exit codes: 0 = both valid, 1 = at least one invalid, 2 = claude CLI missing.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_JSON="$ROOT/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$ROOT/.claude-plugin/marketplace.json"

if ! command -v claude >/dev/null 2>&1; then
  echo "✘ claude CLI not found in PATH" >&2
  exit 2
fi

fail=0

for f in "$PLUGIN_JSON" "$MARKETPLACE_JSON"; do
  if [[ ! -f "$f" ]]; then
    echo "✘ missing: $f" >&2
    fail=1
    continue
  fi
  echo "→ validating ${f#$ROOT/}"
  if ! claude plugin validate "$f"; then
    fail=1
  fi
  echo
done

if [[ $fail -ne 0 ]]; then
  echo "✘ validation failed — fix before committing" >&2
  exit 1
fi

echo "✔ all manifests valid"
