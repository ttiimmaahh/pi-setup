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
  - `pi-tool-chrome/config.json`
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

```bash
git clone https://github.com/ttiimmaahh/pi-setup.git
cd pi-setup
bash apply.sh
```

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
bash scripts/security_scan.py
```

Review the diff before committing.

## Local package paths

Some package entries may point at local development repos. The scripts warn when they find entries like:

```text
../../Developer/gitroot/personal/pi-extensions/pi-tool-chrome
../../Developer/gitroot/personal/pi-usage-bar
../../Developer/gitroot/personal/pi-extensions/pi-qol
```

Those paths must exist on any target machine, or the entries should be replaced with npm/git package specs. See [`docs/local-packages.md`](docs/local-packages.md).

## Files

```text
apply.sh                         # restore config/ into ~/.pi/agent/
export.sh                        # export auth-free ~/.pi/agent config into config/
config/                          # portable Pi configuration snapshot
scripts/export_portable_pi_config.py
scripts/check_local_package_paths.py
scripts/security_scan.py          # conservative pre-commit/publication scan
docs/security.md
docs/local-packages.md
docs/extensions.md
```
