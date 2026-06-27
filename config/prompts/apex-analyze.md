---
description: Analyze a single full APEX SQL export and write reusable findings
argument-hint: "[path/to/full-apex-export.sql]"
---

Analyze the developer's single full APEX application export without database access. Run this before `/apex-generate` or `/apex-change`.

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
3. Run the full analyzer:
   ```bash
   python3 "<skill-dir>/scripts/analyze_apex_export.py" <source.sql> apex-analysis
   ```
4. Optional quick terminal summary when useful:
   ```bash
   python3 "<skill-dir>/scripts/summarize_apex_export.py" <source.sql>
   ```
5. Confirm the analysis outputs exist:
   ```text
   apex-analysis/findings.json
   apex-analysis/apex-overview.md
   apex-analysis/pages.md
   apex-analysis/safe-edit-targets.md
   apex-analysis/pages.csv
   apex-analysis/regions.csv
   apex-analysis/source-index.csv
   ```
6. Confirm `.apex-workflow-skill`, `AGENTS.md`, and `CLAUDE.md` exist in the project root (the analyzer creates any that are missing; it never overwrites existing ones).
7. Report key findings:
   - Application ID/name.
   - Page count.
   - Region/item/process/dynamic action counts.
   - Notable safe edit targets.
   - Any ambiguity such as multiple exports or missing pages.
8. Tell the developer the next normal command is `/apex-generate`.

Do not modify the source export. Do not run database tools.
