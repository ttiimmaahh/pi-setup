#!/usr/bin/env python3
"""Conservative pre-commit/publication scan for accidental Pi secrets/state.

The scan covers:
- current working-tree files, including untracked files
- reachable Git history from all refs, when run inside a Git repo

It intentionally does not scan the `.git` object database directly. Reachable history is
scanned through Git. Dangling/unreachable local objects are not part of the published repo.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

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
    ("Anthropic API key", re.compile(r"sk-ant-[A-Za-z0-9_-]+")),
    ("OpenAI project key", re.compile(r"sk-proj-[A-Za-z0-9_-]+")),
    ("GitHub classic token", re.compile(r"ghp_[A-Za-z0-9_]+")),
    ("GitHub fine-grained token", re.compile(r"github_pat_[A-Za-z0-9_]+")),
    ("Authorization header value", re.compile(r"Bearer\s+[A-Za-z0-9._=-]+")),
    ("access/refresh token assignment", re.compile(r"\b(?:access|refresh)_token\b\s*[:=]", re.I)),
    ("client secret assignment", re.compile(r"\bclient_secret\b\s*[:=]", re.I)),
    ("private key block", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA |)?PRIVATE KEY-----")),
]

SENSITIVE_JSON_KEYS = re.compile(
    r"^(?:apiKey|api_key|token|accessToken|refreshToken|password|secret|clientSecret|auth)$",
    re.I,
)

ALLOW_ENV_VAR_VALUE = re.compile(r"^\$[A-Z][A-Z0-9_]*$")


def is_binary_bytes(data: bytes) -> bool:
    return b"\0" in data[:4096]


def is_binary(path: Path) -> bool:
    try:
        return is_binary_bytes(path.read_bytes())
    except OSError:
        return True


def normalized_parts(path: str | Path | PurePosixPath) -> tuple[str, ...]:
    if isinstance(path, Path):
        try:
            return path.relative_to(ROOT).parts
        except ValueError:
            return path.parts
    return PurePosixPath(str(path)).parts


def path_findings(path: str | Path | PurePosixPath) -> list[str]:
    findings = []
    for part in normalized_parts(path):
        if part in BANNED_PATH_PARTS:
            findings.append(f"banned path component: {part}")
    return findings


def text_findings(path: PurePosixPath, text: str) -> list[str]:
    findings = []
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(f"secret-like text matched: {label}")
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


def json_findings(path: PurePosixPath, text: str) -> list[str]:
    if path.suffix != ".json":
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]
    return scan_json_value(data)


def scan_text_blob(path: PurePosixPath, text: str) -> list[str]:
    findings = path_findings(path)
    findings.extend(text_findings(path, text))
    findings.extend(json_findings(path, text))
    return findings


def scan_working_tree() -> dict[str, list[str]]:
    findings_by_file = {}
    for path in ROOT.rglob("*"):
        if path.is_dir():
            continue
        if ".git" in path.parts:
            continue

        rel = PurePosixPath(path.relative_to(ROOT).as_posix())
        findings = path_findings(rel)
        if not is_binary(path):
            text = path.read_text(encoding="utf-8", errors="ignore")
            findings.extend(text_findings(rel, text))
            findings.extend(json_findings(rel, text))

        if findings:
            findings_by_file[f"working-tree:{rel}"] = findings
    return findings_by_file


def git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def is_git_repo() -> bool:
    return git(["rev-parse", "--is-inside-work-tree"], check=False).returncode == 0


def git_blob_bytes(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout


def scan_git_history() -> dict[str, list[str]]:
    findings_by_file = {}
    if not is_git_repo():
        return findings_by_file

    commits = git(["rev-list", "--all"]).stdout.splitlines()
    for commit in commits:
        paths_raw = git(["ls-tree", "-r", "--name-only", "-z", commit]).stdout
        paths = [path for path in paths_raw.split("\0") if path]
        for path in paths:
            rel = PurePosixPath(path)
            findings = path_findings(rel)
            data = git_blob_bytes(commit, path)
            if not is_binary_bytes(data):
                text = data.decode("utf-8", errors="ignore")
                findings.extend(text_findings(rel, text))
                findings.extend(json_findings(rel, text))
            if findings:
                findings_by_file[f"git-history:{commit[:12]}:{rel}"] = findings
    return findings_by_file


def print_findings(findings_by_file: dict[str, list[str]]) -> None:
    print("Security scan failed:")
    for path, findings in sorted(findings_by_file.items()):
        print(f"\n{path}")
        for finding in findings:
            print(f"  - {finding}")


def main() -> int:
    findings_by_file = {}
    findings_by_file.update(scan_working_tree())
    findings_by_file.update(scan_git_history())

    if findings_by_file:
        print_findings(findings_by_file)
        return 1

    print("Security scan passed. Working tree and reachable Git history are clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
