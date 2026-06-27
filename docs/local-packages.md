# Local Pi package paths

Pi supports local package entries in `settings.json`. They are useful during extension development, but they are not fully portable unless the same paths exist on the target machine.

This public setup intentionally excludes local package paths from `config/settings.json` so `npx github:ttiimmaahh/pi-setup` works for other users.

## Export behavior

`export.sh` / `Export.ps1` drop local package entries by default when refreshing `config/settings.json`. They also export empty public placeholders for `models.json` and `mcp.json` unless explicitly overridden.

To keep local paths during a private export, run:

```bash
PI_SETUP_INCLUDE_LOCAL_PACKAGES=1 bash export.sh
```

On PowerShell:

```powershell
$env:PI_SETUP_INCLUDE_LOCAL_PACKAGES = "1"
powershell -ExecutionPolicy Bypass -File .\Export.ps1
```

To keep local model or MCP config during a private export, set:

```bash
PI_SETUP_INCLUDE_MODELS=1 PI_SETUP_INCLUDE_MCP=1 bash export.sh
```

On PowerShell:

```powershell
$env:PI_SETUP_INCLUDE_MODELS = "1"
$env:PI_SETUP_INCLUDE_MCP = "1"
powershell -ExecutionPolicy Bypass -File .\Export.ps1
```

Only use these flags for private/local branches. Do not publish local machine paths, model defaults, or MCP endpoints in the public setup unless they are intentionally part of the documented workflow.

## Options for local development packages

### Keep local paths privately

Good for personal machines where a common directory layout is cloned consistently.

Trade-off: new machines need those sibling repos cloned in the expected locations.

### Replace with npm package specs

Good when the package is published to npm:

```json
"npm:example-pi-package"
```

Trade-off: less convenient for local development versions.

### Replace with git package specs

Good when the package is public/private on GitHub:

```json
"git:github.com/user/example-pi-package@v1.0.0"
```

Prefer pinned tags or commits for reproducibility.
