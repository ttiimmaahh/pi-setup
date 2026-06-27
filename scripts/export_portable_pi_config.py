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
}
LOCAL_PATH_HINT_RE = re.compile(r"^(?:\.|/|~)")

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
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


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


def sanitize_models(models):
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
        print("Excluded local package paths from exported public config:")
        for source in dropped:
            print(f"  - {source}")
        print("Set PI_SETUP_INCLUDE_LOCAL_PACKAGES=1 to keep them during export.")
    return settings


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: export_portable_pi_config.py PI_DIR OUT_DIR", file=sys.stderr)
        return 2

    pi_dir = Path(sys.argv[1]).expanduser()
    out_dir = Path(sys.argv[2]).expanduser()

    for stale_path in STALE_LOCAL_ONLY_PATHS:
        destination = out_dir / stale_path
        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()

    settings_path = pi_dir / "settings.json"
    if settings_path.exists():
        settings = load_json(settings_path)
        portable_settings = {
            key: value
            for key, value in settings.items()
            if key not in DROP_SETTINGS_KEYS and not SECRET_KEY_RE.search(key)
        }
        if os.environ.get("PI_SETUP_INCLUDE_LOCAL_PACKAGES") != "1":
            portable_settings = drop_local_package_entries(portable_settings)
        write_json(out_dir / "settings.json", portable_settings)

        local_packages = find_local_package_hints(portable_settings)
        if local_packages:
            print("Warning: settings.json contains local package paths that must exist on the target machine:")
            for source in local_packages:
                print(f"  - {source}")

    for file_name in PORTABLE_FILES:
        source = pi_dir / file_name
        if source.exists():
            destination = out_dir / file_name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    models_path = pi_dir / "models.json"
    if models_path.exists():
        write_json(out_dir / "models.json", sanitize_models(load_json(models_path)))

    mcp_path = pi_dir / "mcp.json"
    if mcp_path.exists():
        write_json(out_dir / "mcp.json", strip_auth_fields(load_json(mcp_path)))

    for directory_name in PORTABLE_DIRS:
        source = pi_dir / directory_name
        destination = out_dir / directory_name
        if not source.exists():
            continue
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))

    print(f"Exported portable Pi config from {pi_dir} to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
