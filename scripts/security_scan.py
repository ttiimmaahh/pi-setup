#!/usr/bin/env python3
"""Conservative pre-commit/publication scan for accidental Pi secrets/state."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BANNED_PATH_PARTS = {
    "auth.json",
    "mcp-oauth",
    "sessions",
    "usage",
    "run-history.jsonl",
    "trust.json",
    "mcp-cache.json",
    "mcp-onboarding.json",
    "projects-memory",
    "pi-hermes-memory",
    "sessions.db",
    "sessions.db-shm",
    "sessions.db-wal",
    "node_modules",
    ".env",
}

SECRET_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]+"),
    re.compile(r"sk-proj-[A-Za-z0-9_-]+"),
    re.compile(r"ghp_[A-Za-z0-9_]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"Bearer\s+[A-Za-z0-9._=-]+"),
    re.compile(r"\b(?:access|refresh)_token\b", re.I),
    re.compile(r"\bclient_secret\b", re.I),
]

SENSITIVE_JSON_KEYS = re.compile(
    r"^(?:apiKey|api_key|token|accessToken|refreshToken|password|secret|clientSecret|auth)$",
    re.I,
)

ALLOW_ENV_VAR_VALUE = re.compile(r"^\$[A-Z][A-Z0-9_]*$")


def is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return True
    return b"\0" in chunk


def path_findings(path: Path) -> list[str]:
    rel_parts = path.relative_to(ROOT).parts
    findings = []
    for part in rel_parts:
        if part in BANNED_PATH_PARTS:
            findings.append(f"banned path component: {part}")
    return findings


def text_findings(path: Path, text: str) -> list[str]:
    findings = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(f"secret-like text matched: {pattern.pattern}")
    return findings


def scan_json_value(value, breadcrumb: str = "") -> list[str]:
    findings = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{breadcrumb}.{key}" if breadcrumb else key
            if SENSITIVE_JSON_KEYS.search(key):
                if not (isinstance(child, str) and ALLOW_ENV_VAR_VALUE.match(child)):
                    findings.append(f"sensitive JSON key has non-env value: {child_path}")
            findings.extend(scan_json_value(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(scan_json_value(child, f"{breadcrumb}[{index}]"))
    return findings


def json_findings(path: Path, text: str) -> list[str]:
    if path.suffix != ".json":
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]
    return scan_json_value(data)


def main() -> int:
    findings_by_file = {}
    for path in ROOT.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts:
            continue

        findings = path_findings(path)
        if not is_binary(path):
            text = path.read_text(encoding="utf-8", errors="ignore")
            findings.extend(text_findings(path, text))
            findings.extend(json_findings(path, text))

        if findings:
            findings_by_file[path.relative_to(ROOT)] = findings

    if findings_by_file:
        print("Security scan failed:")
        for path, findings in findings_by_file.items():
            print(f"\n{path}")
            for finding in findings:
                print(f"  - {finding}")
        return 1

    print("Security scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
