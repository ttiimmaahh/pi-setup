---
name: review-global-agents
description: Audit and improve a user's global Pi AGENTS.md against a portable orchestration baseline, preserving intentional local model routing and tool choices. Use when reviewing, creating, merging, sanitizing, or modernizing ~/.pi/agent/AGENTS.md, especially before adopting pi-setup's example guidance.
---

# Review Global AGENTS.md

Help the user produce a coherent global instruction file; do not mechanically append
or overwrite policy text.

## Safety contract

- Resolve the target as `${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/AGENTS.md`.
- Treat the existing file as user-owned. Never replace it without explicit approval.
- Do not expose secrets or unnecessary personal details in analysis, drafts, or logs.
- Draft in a temporary file first. Before an approved write, create a timestamped
  sibling backup such as `AGENTS.md.backup-YYYYMMDD-HHMMSS`.
- If the target is missing, still review the proposed new file before creating it.

## Workflow

1. Read `references/AGENTS.example.md` completely.
2. Read `references/ORCHESTRATION_REVIEW.md` before evaluating delegation or
   model-routing rules.
3. Inspect the target and every local file it explicitly tells agents to load. Report
   missing references; audit referenced files for relevance and portability without
   absorbing unrelated domain content into the global file.
4. Establish the user's environment and intent: available models/providers and
   harnesses, orchestration tools, Herdr usage, preferred writer/reviewer topology,
   risk level, and whether the result is private or publishable. Infer only what
   current files or commands prove; ask about consequential unknowns.
5. Ask whether to **adopt the example matrix**, **customize the matrix**, or use
   **capability roles only**. For customization, gather each model's alias, provider,
   invocation harness, relative cost/intelligence/taste scores, preferred and excluded
   roles, effort/context defaults, fallback, and escalation path. Also identify the
   primary orchestrator and independent reviewer choices. Explain that scores are
   relative judgments, not objective benchmarks; do not force the user to score an
   axis they do not find useful.
6. Produce an audit grouped as **Keep**, **Adapt**, **Add**, **Remove**, and
   **Conflicts/questions**. Cover privacy, stale assumptions, instruction precedence,
   portability, model roles, delegation, permissions, validation, and context cost.
7. Explain trade-offs and ask the user to choose among material policy conflicts.
   Preserve intentional local specialization instead of flattening it into generic
   advice.
8. Draft one internally consistent candidate. Keep global guidance about how agents
   work; move stack/project procedures to on-demand references or skills.
9. Validate the draft using the checklist below, then show a concise summary and a
   diff against the current target.
10. Ask for explicit approval to write. On approval, back up the target, write the
   candidate atomically where practical, and report both paths. On rejection, leave
   the target untouched and offer the draft path.

## Validation checklist

- No secret, PII, retired client, or unjustified machine-specific detail.
- No missing referenced files or unavailable mandatory tools/models.
- Every routing alias appears in the matrix or capability-role definitions; every
  mandatory specialist has a verified harness and fallback.
- Model choice follows an explicit quality floor; cost never overrides required
  correctness, and important UI work covers both experience and integration quality.
- One clear parent authority and one-writer rule for each active worktree.
- Delegates have roles, compact contracts, bounded scope, and stop conditions.
- Fresh review is independent; inherited context is used only when needed.
- Herdr routing is conditional on both installation and `HERDR_ENV=1`.
- Permission boundaries and destructive-operation rules are explicit.
- Completion requires relevant diagnostics/tests, diff review, and residual risks.
- Defaults scale with task risk; trivial work is not forced through ceremony.
- No contradictory, duplicated, or obsolete instructions remain.
