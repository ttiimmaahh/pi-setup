# Local Pi package paths

Pi supports local package entries in `settings.json`. They are useful during extension development, but they are not fully portable unless the same paths exist on the target machine.

Current local package entries may include:

```text
../../Developer/gitroot/personal/pi-extensions/pi-tool-chrome
../../Developer/gitroot/personal/pi-usage-bar
../../Developer/gitroot/personal/pi-extensions/pi-qol
```

## Options

### Keep local paths

Good for personal machines where `~/Developer/gitroot/personal` is cloned consistently.

Trade-off: new machines need those sibling repos cloned in the expected locations.

### Replace with npm package specs

Good when the package is published to npm:

```json
"npm:pi-usage-bar"
```

Trade-off: less convenient for local development versions.

### Replace with git package specs

Good when the package is public/private on GitHub:

```json
"git:github.com/ttiimmaahh/pi-extensions@main"
```

Prefer pinned tags or commits for reproducibility.

## Script behavior

`apply.sh` and `export.sh` warn about local paths but do not block. This keeps the repo usable while making non-portable entries obvious.
