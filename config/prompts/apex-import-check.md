---
description: Preflight check before a developer imports generated APEX SQL in App Builder
argument-hint: "path/to/generated.sql"
---

Prepare for a human-run APEX UI import. Do not import automatically and do not use database credentials.

Developer input: `$ARGUMENTS`

Agent checklist:
1. Require or identify a generated SQL path under `apex-exports/generated/`.
2. Confirm the generated SQL file exists.
3. Confirm the sibling manifest exists:
   ```text
   <generated.sql>.patch-manifest.json
   ```
4. Confirm the baseline `.sql` export under `apex-exports/ui/` remains unchanged.
5. Confirm the patch spec path under `apex-exports/patch-specs/` if known.
6. Tell the developer to import in APEX App Builder with:
   - File type: `Application, Page or Component Export`
   - File character set: `Unicode UTF-8`
7. Tell the developer to verify workspace, target app, parsing schema, app ID, and install option before final install.
8. After import, tell the developer to run `/apex-test-result` to record pass/fail and notes.
