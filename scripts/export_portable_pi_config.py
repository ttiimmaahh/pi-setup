#!/usr/bin/env python3
"""Export an auth-free, portable Pi configuration snapshot."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

SECRET_KEY_RE = re.compile(r"(auth|token|secret|password|credential|cookie|refresh|access)", re.I)
DROP_SETTINGS_KEYS = {
    "lastChangelogVersion",
    "trackingId",
    # Public setup should not force a user's provider/model choice.
    "defaultProvider",
    "defaultModel",
}
LOCAL_PATH_HINT_RE = re.compile(r"^(?:\.|[/\\]|~|[A-Za-z]:[/\\])")

# Friendly defaults for known local-only providers. Pi accepts env-var references
# like "$LMSTUDIO_API_KEY" in models.json, which keeps the file portable.
PROVIDER_API_KEY_ENV = {
    "lmstudio": "$LMSTUDIO_API_KEY",
    "mlx": "$MLX_API_KEY",
}

PORTABLE_FILES = (
    "keybindings.json",
    "pi-handoff-config.json",
    "pi-usage-bar/config.json",
)

PORTABLE_DIRS = (
    "prompts",
    "extensions",
    "skills",
    "themes",
)

STALE_LOCAL_ONLY_PATHS = (
    "pi-tool-chrome",
)

IGNORE_PATTERNS = (
    ".DS_Store",
    "node_modules",
    ".git",
    "*.log",
    ".env",
    ".env.*",
    # Work-specific prompt templates should not be exported to the public personal setup.
    "apex-*.md",
    # Herdr installs and upgrades this host-integration shim itself.
    "herdr-agent-state.ts",
)


def load_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read valid JSON from {path}: {exc}") from exc


def remove_existing(path: Path) -> None:
    if not path.exists():
        return
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    except OSError as exc:
        raise RuntimeError(f"Could not remove stale export path {path}: {exc}") from exc


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(data, indent=2, sort_keys=False) + "\n")
    except OSError as exc:
        raise RuntimeError(f"Could not write exported JSON to {path}: {exc}") from exc


def strip_auth_fields(value):
    if isinstance(value, dict):
        return {
            key: strip_auth_fields(child)
            for key, child in value.items()
            if not SECRET_KEY_RE.search(key)
        }
    if isinstance(value, list):
        return [strip_auth_fields(child) for child in value]
    return value


def sanitize_mcp_config(mcp_config):
    if os.environ.get("PI_SETUP_INCLUDE_MCP") != "1":
        return {"imports": [], "mcpServers": {}}
    return strip_auth_fields(mcp_config)


def sanitize_handoff_config(config):
    if isinstance(config, dict):
        # Let pi-handoff auto-pick a cheap available model for each user's setup.
        config.pop("model", None)
    return config


def sanitize_models(models):
    if os.environ.get("PI_SETUP_INCLUDE_MODELS") != "1":
        return {"providers": {}}

    providers = models.get("providers")
    if not isinstance(providers, dict):
        return models

    for provider_name, provider in providers.items():
        if not isinstance(provider, dict) or "apiKey" not in provider:
            continue
        api_key = provider.get("apiKey")
        if isinstance(api_key, str) and api_key.startswith("$"):
            continue
        env_name = provider_name.upper().replace("-", "_")
        provider["apiKey"] = PROVIDER_API_KEY_ENV.get(provider_name, f"${env_name}_API_KEY")
    return models


def package_source(entry) -> str | None:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        source = entry.get("source")
        if isinstance(source, str):
            return source
    return None


def find_local_package_hints(settings) -> list[str]:
    hints = []
    if not isinstance(settings, dict):
        return hints
    for entry in settings.get("packages", []):
        source = package_source(entry)
        if source and LOCAL_PATH_HINT_RE.search(source):
            hints.append(source)
    return hints


def info(message: str) -> None:
    sys.stdout.write(f"{message}\n")


def drop_local_package_entries(settings):
    if not isinstance(settings, dict):
        return settings
    packages = settings.get("packages")
    if not isinstance(packages, list):
        return settings

    filtered = []
    dropped = []
    for entry in packages:
        source = package_source(entry)
        if source and LOCAL_PATH_HINT_RE.search(source):
            dropped.append(source)
        else:
            filtered.append(entry)

    settings["packages"] = filtered
    if dropped:
        info("Excluded local package paths from exported public config:")
        for source in dropped:
            info(f"  - {source}")
        info("Set PI_SETUP_INCLUDE_LOCAL_PACKAGES=1 to keep them during export.")
    return settings


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: export_portable_pi_config.py PI_DIR OUT_DIR\n")
        return 2

    pi_dir = Path(sys.argv[1]).expanduser()
    out_dir = Path(sys.argv[2]).expanduser()

    for stale_path in STALE_LOCAL_ONLY_PATHS:
        remove_existing(out_dir / stale_path)

    settings_path = pi_dir / "settings.json"
    settings_destination = out_dir / "settings.json"
    remove_existing(settings_destination)
    if settings_path.exists():
        settings = load_json(settings_path)
        portable_settings = {
            key: value
            for key, value in settings.items()
            if key not in DROP_SETTINGS_KEYS and not SECRET_KEY_RE.search(key)
        }
        if os.environ.get("PI_SETUP_INCLUDE_LOCAL_PACKAGES") != "1":
            portable_settings = drop_local_package_entries(portable_settings)
        write_json(settings_destination, portable_settings)

        local_packages = find_local_package_hints(portable_settings)
        if local_packages:
            info("Warning: settings.json contains local package paths that must exist on the target machine:")
            for source in local_packages:
                info(f"  - {source}")

    for file_name in PORTABLE_FILES:
        source = pi_dir / file_name
        destination = out_dir / file_name
        remove_existing(destination)
        if source.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    models_path = pi_dir / "models.json"
    models = load_json(models_path) if models_path.exists() else {"providers": {}}
    write_json(out_dir / "models.json", sanitize_models(models))

    mcp_path = pi_dir / "mcp.json"
    mcp_config = load_json(mcp_path) if mcp_path.exists() else {"imports": [], "mcpServers": {}}
    write_json(out_dir / "mcp.json", sanitize_mcp_config(mcp_config))

    handoff_path = out_dir / "pi-handoff-config.json"
    if handoff_path.exists():
        write_json(handoff_path, sanitize_handoff_config(load_json(handoff_path)))

    for directory_name in PORTABLE_DIRS:
        source = pi_dir / directory_name
        destination = out_dir / directory_name
        # Reconcile removals as well as additions. Otherwise a deleted live
        # resource directory remains forever in the exported snapshot.
        remove_existing(destination)
        if not source.exists():
            continue
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))
        if not any(destination.rglob("*")):
            remove_existing(destination)

    info(f"Exported portable Pi config from {pi_dir} to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
