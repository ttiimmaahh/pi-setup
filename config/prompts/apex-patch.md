---
description: Low-level helper for applying an existing APEX JSON patch spec
argument-hint: "path/to/patch-spec.json"
---

This is a low-level maintenance command. Developers should normally use `/apex-change "describe the UI change"` instead.

Use `/apex-patch` only when a JSON patch spec already exists and you need to apply it without interpreting a natural-language UI request.

Developer input: `$ARGUMENTS`

Agent steps:
1. Require a patch spec path in `$ARGUMENTS`. If none is provided, redirect the developer to `/apex-change`.
2. Resolve the skill directory:
   - Prefer `$(cat .apex-workflow-skill)` when present.
   - In Claude Code, fall back to `~/.claude/skills/apex-single-file-ui-workflow`.
   - In Pi or compatible harnesses, fall back to `~/.agents/skills/apex-single-file-ui-workflow`.
   - Otherwise use the installed `apex-single-file-ui-workflow` skill path available to the agent.
3. Read the spec and confirm it only uses currently supported ops:
   - `setRegionTitle`
   - `setPageTitle`
   - `setNavigationLabel`
4. Apply it:
   ```bash
   python3 "<skill-dir>/scripts/apply_apex_mockup_patch.py" <patch-spec.json>
   ```
5. Verify the baseline source export under `apex-exports/ui/` did not change.
6. Report generated SQL and manifest under `apex-exports/generated/`.
7. Recommend `/apex-import-check <generated.sql>`.
