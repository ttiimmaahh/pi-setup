---
description: Optional one-time scaffold for a project that has not been set up for the APEX single-file workflow
---

This is optional setup scaffolding, not the normal developer loop. Do not present it as the first command a developer must run if the project already has the expected folders/files.

Normal developer loop:

```text
/apex-analyze -> /apex-generate -> /apex-change -> /apex-import-check -> /apex-test-result
```

Use `/apex-bootstrap` only when the current project is missing the basic workflow structure.

Agent steps:
1. Locate the installed skill directory for `apex-single-file-ui-workflow`.
2. Run its bootstrap script against the current project root:
   ```bash
   python3 <skill-dir>/scripts/bootstrap_apex_single_file_project.py .
   ```
3. Confirm `.apex-workflow-skill` was created and points to the skill.
4. Confirm `AGENTS.md` and `CLAUDE.md` were created (existing files are left untouched; mention that to the developer if they already existed).
5. Confirm `apex-exports/ui/`, `apex-exports/patch-specs/`, `apex-exports/generated/`, `apex-analysis/` readiness, `mockups/apex-prototype/`, and `apex-test-results/`.
6. If exactly one `.sql` export exists under `apex-exports/ui/`, recommend `/apex-analyze` next.
7. If no export exists, tell the developer to export the full APEX application as a single `.sql` file into `apex-exports/ui/`, then run `/apex-analyze`.

Do not copy workflow Python scripts into the project. They stay in the installed skill.
