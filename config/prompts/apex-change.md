---
description: Apply a requested APEX UI change, preview it in the mockup, and produce importable SQL
argument-hint: "Describe the UI change to make"
---

Use this command when the developer describes an actual UI change to make from the generated APEX mockup/model.

Developer input: `$ARGUMENTS`

Agent contract:
- Work from the immutable single-file export under `apex-exports/ui/` unless the user explicitly names another source export.
- Use `apex-analysis/` and `mockups/apex-prototype/data/export-derived.js` to identify the target page/component.
- For design/styling/component requests, consult the skill's Universal Theme 24.2 design package under `references/ut-24.2/` to map the request to APEX/UT concepts before deciding whether a supported patch operation exists.
- Only generate importable SQL under `apex-exports/generated/`.
- Do not mutate the baseline export in `apex-exports/ui/`.

Agent steps:
1. Resolve the skill directory:
   - Prefer `$(cat .apex-workflow-skill)` when present.
   - In Claude Code, fall back to `~/.claude/skills/apex-single-file-ui-workflow`.
   - In Pi or compatible harnesses, fall back to `~/.agents/skills/apex-single-file-ui-workflow`.
   - Otherwise use the installed `apex-single-file-ui-workflow` skill path available to the agent.
2. Ensure there is exactly one baseline `.sql` export under `apex-exports/ui/`, unless the user supplied an explicit source path.
3. Ensure analysis exists. If `apex-analysis/findings.json` or `apex-analysis/apex-overview.md` is missing or older than the source export, run:
   ```bash
   python3 "<skill-dir>/scripts/analyze_apex_export.py" <source.sql> apex-analysis
   ```
4. Ensure the mockup model exists. If `mockups/apex-prototype/data/export-derived.js` is missing or older than the source export, run:
   ```bash
   python3 "<skill-dir>/scripts/generate_apex_prototype.py" <source.sql>
   ```
5. If the request mentions design, styling, layout, components, icons, templates, utility classes, JavaScript behavior, or Universal Theme behavior, read the relevant files under `<skill-dir>/references/ut-24.2/`:
   - Start with `ut-24.2-design-guide.md` and `component-catalog.json`.
   - Use `css-utilities.md` and `css-inventory.json` for responsive classes, status/color utilities, CSS variables, and Font APEX classes.
   - Use `raw/` snapshots only for spot checks; some pages are partial because the public APEX app intermittently rate-limited scraping.
6. Interpret the developer request against currently supported safe patch operations:
   - `setRegionTitle` for an existing region title.
   - `setPageTitle` for an existing page name/title.
   - `setNavigationLabel` for an existing navigation menu item label.
   - `addButton` for adding a simple button to an existing page/region.
   - `addButtonAlert` for adding a simple button to an existing page/region that opens a JavaScript `alert(...)` through a click dynamic action.
7. If the request needs an unsupported operation, stop and explain the gap, including the likely export fields or UT concept from the design package when known. Do not fake it by editing only HTML/CSS or by manually inventing APEX IDs outside the supported patch generator.
8. Create a descriptive JSON patch spec in `apex-exports/patch-specs/`, for example:
   ```text
   apex-exports/patch-specs/change-<page-or-component>-<short-name>.json
   ```
9. Set `sourceRoot` to the baseline source export and `outputRoot` to a new file under `apex-exports/generated/`. Use `overwrite: false` unless intentionally replacing a prior generated file.
10. Apply the patch:
   ```bash
   python3 "<skill-dir>/scripts/apply_apex_mockup_patch.py" apex-exports/patch-specs/<spec>.json
   ```
11. Regenerate the mockup from the generated SQL file so the browser preview reflects the import candidate:
    ```bash
    python3 "<skill-dir>/scripts/generate_apex_prototype.py" apex-exports/generated/<generated>.sql mockups/apex-prototype
    ```
12. Verify the source export under `apex-exports/ui/` did not change.
13. Report:
    - The interpreted change.
    - The target page/component identifiers used.
    - The patch spec path.
    - The generated SQL path.
    - The patch manifest path.
    - The mockup preview path (`mockups/apex-prototype/index.html`).
    - Any residual risks or import notes.

Recommended next command: `/apex-import-check <generated-sql-path>`.
