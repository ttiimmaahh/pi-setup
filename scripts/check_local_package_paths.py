#!/usr/bin/env python3
"""Warn when Pi settings reference local package paths."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LOCAL_PATH_RE = re.compile(r"^(?:\.|/|~)")


def package_source(entry) -> str | None:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        source = entry.get("source")
        if isinstance(source, str):
            return source
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check_local_package_paths.py SETTINGS_JSON", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        return 0

    settings = json.loads(path.read_text(encoding="utf-8"))
    local_packages = []
    for entry in settings.get("packages", []):
        source = package_source(entry)
        if source and LOCAL_PATH_RE.search(source):
            local_packages.append(source)

    if local_packages:
        print("\nNote: these Pi package entries are local paths and must exist on this target machine:")
        for source in local_packages:
            print(f"  - {source}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
