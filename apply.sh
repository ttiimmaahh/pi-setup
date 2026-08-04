#!/usr/bin/env bash
# Apply this repo's portable Pi setup to the current machine.
# Auth is deliberately not restored. After this runs, use `pi /login` or set
# provider-specific API key environment variables as needed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/config"
PI_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
PI_LENS_CONFIG_PATH="${PI_LENS_CONFIG_PATH:-$HOME/.pi-lens/config.json}"
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

install_pi_lens_config() {
  local source="$SOURCE_DIR/pi-lens/config.json"
  [[ -f "$source" ]] || return 0

  if [[ -e "$PI_LENS_CONFIG_PATH" ]]; then
    mkdir -p "$BACKUP_DIR/pi-lens"
    cp -a "$PI_LENS_CONFIG_PATH" "$BACKUP_DIR/pi-lens/config.json"
  fi

  mkdir -p "$(dirname "$PI_LENS_CONFIG_PATH")"
  cp "$source" "$PI_LENS_CONFIG_PATH"
  echo "  installed Pi Lens config -> $PI_LENS_CONFIG_PATH"
}

install_file settings.json
install_file keybindings.json
install_file models.json
install_file mcp.json
install_file pi-handoff-config.json
install_file pi-usage-bar/config.json

install_dir prompts
install_dir extensions
install_dir skills
install_dir themes
install_pi_lens_config

install_web_tools_dependencies() {
  local extension_dir="$PI_DIR/extensions/web-tools"
  [[ -f "$extension_dir/package-lock.json" ]] || return 0

  if ! command -v npm >/dev/null 2>&1; then
    echo "npm is required to install the web-tools extension dependencies." >&2
    exit 1
  fi

  echo "  installing extensions/web-tools dependencies"
  npm ci --omit=dev --omit=peer --ignore-scripts --prefix "$extension_dir"
}

install_web_tools_dependencies

MACROPAD_SOURCE="$SOURCE_DIR/macropad"
MACROPAD_TARGET="$HOME/.config/ch57x-keyboard-tool"
if [[ -d "$MACROPAD_SOURCE" ]]; then
  mkdir -p "$MACROPAD_TARGET"
  for filename in coding-voice.yaml coding-voice-ctrl-only-fallback.yaml CHEATSHEET.md; do
    [[ -f "$MACROPAD_SOURCE/$filename" ]] || continue
    if [[ -f "$MACROPAD_TARGET/$filename" ]]; then
      mkdir -p "$BACKUP_DIR/external/ch57x-keyboard-tool"
      cp "$MACROPAD_TARGET/$filename" "$BACKUP_DIR/external/ch57x-keyboard-tool/$filename"
    fi
    cp "$MACROPAD_SOURCE/$filename" "$MACROPAD_TARGET/$filename"
    echo "  installed ~/.config/ch57x-keyboard-tool/$filename"
  done
fi

install_ghostty_macropad_adapter() {
  local source="$MACROPAD_SOURCE/ghostty-f13-adapter.conf"
  [[ -f "$source" ]] || return 0

  local ghostty_dir="${XDG_CONFIG_HOME:-$HOME/.config}/ghostty"
  local adapter="$ghostty_dir/macropad-f13-adapter.conf"
  local config="$ghostty_dir/config"
  mkdir -p "$ghostty_dir" "$BACKUP_DIR/external/ghostty"
  [[ ! -f "$adapter" ]] || cp "$adapter" "$BACKUP_DIR/external/ghostty/macropad-f13-adapter.conf"
  [[ ! -f "$config" ]] || cp "$config" "$BACKUP_DIR/external/ghostty/config"

  cp "$source" "$adapter"
  touch "$config"
  if ! grep -Fqx 'config-file = macropad-f13-adapter.conf' "$config"; then
    printf '\n# pi-setup CH57x portable adapter\nconfig-file = macropad-f13-adapter.conf\n' >>"$config"
  fi

  if command -v ghostty >/dev/null 2>&1; then
    ghostty +validate-config --config-file="$config"
  fi
  echo "  installed Ghostty macropad adapter"
}

install_alacritty_macropad_adapter() {
  local source="$MACROPAD_SOURCE/alacritty-f13-adapter.toml"
  local installer="$SCRIPT_DIR/scripts/install_alacritty_macropad_adapter.js"
  [[ -f "$source" && -f "$installer" ]] || return 0
  if ! command -v node >/dev/null 2>&1; then
    echo "Warning: Node.js is required to install the Alacritty macropad adapter." >&2
    return 0
  fi

  local alacritty_dir="${XDG_CONFIG_HOME:-$HOME/.config}/alacritty"
  node "$installer" \
    --source "$source" \
    --adapter "$alacritty_dir/macropad-f13-adapter.toml" \
    --config "$alacritty_dir/alacritty.toml" \
    --backup-dir "$BACKUP_DIR/external/alacritty"
}

install_claude_macropad_bindings() {
  local source="$MACROPAD_SOURCE/claude-keybindings.json"
  [[ -f "$source" ]] || return 0

  local target="$HOME/.claude/keybindings.json"
  mkdir -p "$(dirname "$target")" "$BACKUP_DIR/external/claude"
  [[ ! -f "$target" ]] || cp "$target" "$BACKUP_DIR/external/claude/keybindings.json"
  cp "$source" "$target"
  echo "  installed Claude Code macropad bindings"
}

install_ghostty_macropad_adapter
install_alacritty_macropad_adapter
install_claude_macropad_bindings

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
