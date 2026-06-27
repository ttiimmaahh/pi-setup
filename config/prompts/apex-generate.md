---
description: Generate or refresh the static APEX mockup from analyzed export data
argument-hint: "[path/to/full-apex-export.sql]"
---

Generate the browser mockup/model from the developer's single full APEX SQL export. This should normally run after `/apex-analyze`.

Developer input: `$ARGUMENTS`

Agent steps:
1. Resolve the source export:
   - Use `$ARGUMENTS` when provided.
   - Otherwise require exactly one `.sql` file under `apex-exports/ui/`.
2. Resolve the skill directory:
   - Prefer `$(cat .apex-workflow-skill)` when present.
   - In Claude Code, fall back to `~/.claude/skills/apex-single-file-ui-workflow`.
   - In Pi or compatible harnesses, fall back to `~/.agents/skills/apex-single-file-ui-workflow`.
   - Otherwise use the installed `apex-single-file-ui-workflow` skill path available to the agent.
3. Ensure analysis exists. If `apex-analysis/findings.json` or `apex-analysis/apex-overview.md` is missing or older than the source export, run `/apex-analyze` first or run:
   ```bash
   python3 "<skill-dir>/scripts/analyze_apex_export.py" <source.sql> apex-analysis
   ```
4. Generate the prototype:
   ```bash
   python3 "<skill-dir>/scripts/generate_apex_prototype.py" <source.sql>
   ```
5. Confirm output:
   ```text
   mockups/apex-prototype/data/export-derived.js
   mockups/apex-prototype/index.html
   ```
   The generator refreshes `index.html` and `src/` from the skill template on every run; the mockup directory is generated output and should not be hand-edited. The developer can open `index.html` directly in a browser (no local server needed).
6. Report page/list/Interactive Grid counts from the command output or `apex-analysis/findings.json`.
7. Tell the developer the normal next command for real work is:
   ```text
   /apex-change "describe the UI change"
   ```

Do not treat mockup edits as deployed changes. A real UI change must produce generated SQL under `apex-exports/generated/`.
