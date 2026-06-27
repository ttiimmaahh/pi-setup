# Security model

This repo is intended to be safe for a public GitHub repository.

## Allowed

- Pi package/resource settings
- Keyboard shortcuts
- Prompt templates
- Custom skills/extensions/themes that contain no secrets
- MCP server definitions with auth removed
- Model definitions with API keys represented as environment variables, for example `$LMSTUDIO_API_KEY`
- Extension preference files that contain only display/configuration options

## Not allowed

- Pi auth files
- OAuth token directories
- API keys or bearer tokens
- Session logs/transcripts
- Run history
- Usage databases
- Trust decisions
- Memory databases or user/project memories
- Caches
- `.env` files

## Before publishing or pushing

Run:

```bash
bash security-scan.sh
```

On Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\SecurityScan.ps1
```

The scanner checks the current working tree, untracked files, and reachable Git history from all refs.

Also manually review:

```bash
git diff --cached
git status --short
```

The scanner is intentionally conservative. If it fails, either remove the sensitive file/value or change the config to use an environment-variable reference.

## Authentication on a new machine

Authentication is intentionally out of band. After applying this setup, authenticate with Pi directly:

```bash
pi
# /login
```

Or define provider-specific environment variables referenced from `config/models.json`.
