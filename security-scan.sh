#!/usr/bin/env bash
# Run the conservative pre-commit/publication security scan.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  python3 "$SCRIPT_DIR/scripts/security_scan.py"
elif command -v python >/dev/null 2>&1; then
  python "$SCRIPT_DIR/scripts/security_scan.py"
else
  echo "Python 3 was not found. Install Python 3, then rerun this scan." >&2
  exit 127
fi
