# pi-setup

Portable, auth-free setup for my [Pi coding agent](https://pi.dev) configuration.

This repo is designed to be safe to use across macOS and Linux machines. It stores only configuration and resources that are useful on another computer, not credentials or local runtime state.

It also acts as a public index of the Pi extensions I use and maintain. See [`docs/extensions.md`](docs/extensions.md).

## What this restores

`./apply.sh` copies the portable config snapshot from `config/` into `~/.pi/agent/`:

- `settings.json` package/resource configuration
- `keybindings.json`
- `models.json` with API keys represented as environment-variable references
- `mcp.json` with auth fields removed
- prompt templates in `prompts/`
- local `extensions/`, `skills/`, and `themes/` if present
- auth-free extension preference files, currently:
  - `pi-handoff-config.json`
  - `pi-usage-bar/config.json`

## What this never stores

Do **not** commit these Pi files/directories here:

- `auth.json`
- `mcp-oauth/`
- `sessions/`
- `usage/`
- `run-history.jsonl`
- `trust.json`
- `mcp-cache.json`
- `mcp-onboarding.json`
- `projects-memory/`
- `pi-hermes-memory/`
- API keys, OAuth tokens, cookies, passwords, or client secrets

See [`docs/security.md`](docs/security.md) for the public-repo safety model.

## Usage on a new machine

The easiest cross-platform install/apply path is direct from GitHub:

```bash
npx --yes github:ttiimmaahh/pi-setup
```

Preview without writing files:

```bash
npx --yes github:ttiimmaahh/pi-setup -- --dry-run
```

Skip package reconciliation:

```bash
npx --yes github:ttiimmaahh/pi-setup -- --no-update
```

Manual clone/apply still works:

```bash
git clone https://github.com/ttiimmaahh/pi-setup.git
cd pi-setup
bash apply.sh
```

On Windows PowerShell:

```powershell
git clone https://github.com/ttiimmaahh/pi-setup.git
cd pi-setup
powershell -ExecutionPolicy Bypass -File .\Apply.ps1
```

Pi itself requires a bash shell on Windows; [Git for Windows](https://git-scm.com/download/win) is usually enough.

Then authenticate separately:

```bash
pi
# run /login, or configure provider API key environment variables
```

If the Pi CLI is not installed yet:

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

## Refreshing the snapshot from this machine

After changing your Pi setup, run:

```bash
bash export.sh
bash security-scan.sh
```

On Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\Export.ps1
powershell -ExecutionPolicy Bypass -File .\SecurityScan.ps1
```

Review the diff before committing.

## Local package paths

This public setup intentionally excludes local package paths from `config/settings.json` so it works for other users via `npx github:ttiimmaahh/pi-setup`. See [`docs/local-packages.md`](docs/local-packages.md) for the private/local-development escape hatch.

## Releasing

This repo has npm package metadata only so users can run it directly from GitHub with `npx`. It is marked `private` and is not intended for npm registry publication.

Release flow:

```bash
npm version patch   # or minor/major
git push --follow-tags
```

The tag-driven GitHub Action verifies the tag matches `package.json`, runs `npm run check`, and creates a GitHub Release with the direct `npx github:ttiimmaahh/pi-setup` command.

## Files

```text
package.json                     # private npm/npx entrypoint metadata for GitHub npx usage
package-lock.json                # reproducible npm metadata for CI
CHANGELOG.md                     # release notes consumed by GitHub Releases
.github/workflows/ci.yml         # push/PR checks
.github/workflows/release.yml    # tag-driven GitHub Release workflow
bin/pi-setup.js                  # cross-platform Node CLI for npx usage
apply.sh                         # restore config/ into ~/.pi/agent/ on macOS/Linux
export.sh                        # export auth-free ~/.pi/agent config into config/ on macOS/Linux
Apply.ps1                        # PowerShell restore script for Windows
Export.ps1                       # PowerShell export script for Windows
security-scan.sh                 # macOS/Linux security-scan wrapper
SecurityScan.ps1                 # PowerShell security-scan wrapper
config/                          # portable Pi configuration snapshot
scripts/export_portable_pi_config.py
scripts/check_local_package_paths.py
scripts/security_scan.py          # conservative pre-commit/publication scan
docs/security.md
docs/local-packages.md
docs/extensions.md
```
