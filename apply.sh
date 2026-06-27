#!/usr/bin/env bash
# Apply this repo's portable Pi setup to the current machine.
# Auth is deliberately not restored. After this runs, use `pi /login` or set
# provider-specific API key environment variables as needed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/config"
PI_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
BACKUP_DIR="$PI_DIR/backups/$(date +%Y%m%d-%H%M%S)"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "No Pi config snapshot found at $SOURCE_DIR" >&2
  echo "Run ./export.sh on a configured machine first." >&2
  exit 1
fi

mkdir -p "$PI_DIR" "$BACKUP_DIR"

echo "Pi setup: applying portable config from $SOURCE_DIR"
echo "Target: $PI_DIR"

backup_if_exists() {
  local path="$1"
  if [[ -e "$path" ]]; then
    mkdir -p "$BACKUP_DIR/$(dirname "${path#$PI_DIR/}")"
    cp -a "$path" "$BACKUP_DIR/${path#$PI_DIR/}"
  fi
}

install_file() {
  local relative="$1"
  local source="$SOURCE_DIR/$relative"
  local target="$PI_DIR/$relative"
  [[ -f "$source" ]] || return 0
  backup_if_exists "$target"
  mkdir -p "$(dirname "$target")"
  cp "$source" "$target"
  echo "  installed $relative"
}

install_dir() {
  local relative="$1"
  local source="$SOURCE_DIR/$relative"
  local target="$PI_DIR/$relative"
  [[ -d "$source" ]] || return 0
  backup_if_exists "$target"
  rm -rf "$target"
  mkdir -p "$(dirname "$target")"
  cp -a "$source" "$target"
  echo "  installed $relative/"
}

install_file settings.json
install_file keybindings.json
install_file models.json
install_file mcp.json
install_file pi-handoff-config.json
install_file pi-tool-chrome/config.json
install_file pi-usage-bar/config.json

install_dir prompts
install_dir extensions
install_dir skills
install_dir themes

python3 "$SCRIPT_DIR/scripts/check_local_package_paths.py" "$SOURCE_DIR/settings.json" || true

if command -v pi >/dev/null 2>&1; then
  echo ""
  echo "Reconciling Pi package installs from settings.json..."
  if pi list >/dev/null 2>&1; then
    pi update --extensions || {
      echo "Warning: pi update --extensions failed. Check local package paths and network access." >&2
    }
  else
    echo "Warning: pi is installed but 'pi list' failed. Skipping package reconciliation." >&2
  fi
else
  echo ""
  echo "Pi CLI not found. Install it first, then run: pi update --extensions"
fi

echo ""
echo "Auth not restored by design. Re-run /login or configure API-key environment variables on this machine."
echo "Existing files were backed up under: $BACKUP_DIR"
