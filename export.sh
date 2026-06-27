#!/usr/bin/env bash
# Export the portable, auth-free parts of the current Pi setup into this repo.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PI_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
OUT_DIR="$SCRIPT_DIR/config"

if [[ ! -d "$PI_DIR" ]]; then
  echo "Pi config directory not found: $PI_DIR" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

python3 "$SCRIPT_DIR/scripts/export_portable_pi_config.py" "$PI_DIR" "$OUT_DIR"
