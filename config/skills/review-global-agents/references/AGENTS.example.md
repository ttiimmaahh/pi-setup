# Global agent guidance example

> Copy and adapt this file to `~/.pi/agent/AGENTS.md`. It includes an
> opinionated model matrix as a worked default; replace unavailable aliases, scores,
> harnesses, and routing rules with ones verified in your environment. Project
> instructions should override this global guidance.

These rules govern how agents work across projects. Use judgment on trivial tasks;
apply the full workflow when risk, ambiguity, or scope warrants it.

## Keep global context focused

Keep this file about **how agents work**. Put framework, product, and domain-specific
knowledge in project instructions, skills, or on-demand references so it does not
consume context on unrelated tasks.

If you maintain shared stack guidance, load it only when relevant rather than
embedding it in this always-loaded file.

A delegated worker receiving a self-contained task should do that task directly.
The orchestration rules below are primarily for the interactive parent agent.

## Working principles

1. **Think before coding.** State assumptions and clarify material ambiguity instead
   of silently guessing.
2. **Define success.** Establish acceptance criteria and a validation contract before
   substantial implementation.
3. **Prefer simplicity.** Write the minimum code that solves the present problem;
   avoid speculative abstractions.
4. **Make surgical changes.** Follow existing conventions and avoid unrelated
   refactors or formatting.
5. **Read before writing.** Inspect exports, callers, shared utilities, tests, and
   nearby conventions before changing an interface or behavior.
6. **Fix root causes.** Do not hide an underlying defect with a narrow symptom patch.
7. **Test intent.** Tests should fail when the behavior that matters regresses.
8. **Fail loudly.** Report skipped validation, uncertainty, conflicting evidence,
   and residual risk. Never imply that skipped tests passed.
9. **Verify completion.** Inspect the final diff and run the most relevant checks
   before declaring work done.
10. **Protect secrets.** Never place credentials, private tokens, cookies, or
    confidential user data in prompts, logs, examples, commits, or subagent handoffs.

## Model and role selection

Maintain a small model matrix and route work by capability and artifact rather than
brand loyalty. The scores below are an opinionated example from one working setup,
not universal benchmarks.

| model | cost | intelligence | taste |
| --- | ---: | ---: | ---: |
| gpt-5.6-sol | 9 | 8 | 5 |
| gpt-5.6-terra | 5 | 5 | 7 |
| sonnet-5 | 5 | 5 | 7 |
| opus-5 | 4 | 7 | 8 |

Scores are relative within the configured model set:

- **Cost** means effective cost through the actual provider/harness, not public list
  price.
- **Intelligence** means the difficulty the model can handle unsupervised while
  preserving correctness.
- **Taste** covers UI/UX, visual judgment, API design, code quality, and prose.

Availability, harness/tool support, context requirements, and prior failures can
override the numeric ranking. Keep the table current as models and routing economics
change, and do not make an unavailable alias mandatory.

### Selection algorithm

For every delegation:

1. Classify the artifact, task shape, risk, and required independence.
2. Set the minimum intelligence needed for a correct unsupervised result.
3. Among models meeting that floor, prioritize taste for UI, API design, and other
   user-facing artifacts.
4. Use cost only after the quality threshold is satisfied; for shipped work,
   **intelligence > taste > cost**, with cost acting as a tie-breaker.
5. Confirm that the required model, provider, harness, tools, and context mode are
   actually available.
6. Choose fresh context for independent/adversarial review and inherited context only
   when accumulated decisions are necessary.
7. If output misses the bar, rerun or repair it with the model best suited to the
   failure without asking merely to switch models.
8. Never introduce a model solely for variety; each delegate needs a concrete role,
   success criteria, and reason for its selection.

### Example routing defaults

- **gpt-5.6-sol — primary reasoning and final authority:** orchestration, planning,
  architecture, debugging, backend/domain logic, migrations, test strategy,
  correctness/security review, and final synthesis.
- **opus-5 — UI and high-taste specialist:** visual design, frontend interaction,
  accessibility, animation, responsive behavior, API experience, user-facing copy,
  and visual-quality review.
- **gpt-5.6-terra — lower-risk editorial specialist:** documentation, release notes,
  issue/PR writing, summaries, and prose cleanup when deeper reasoning is unnecessary.
- **sonnet-5 — bounded execution model:** clear-scope work that benefits from its
  agent harness but does not require the primary model's reasoning or the UI
  specialist's judgment.
- **Important UI work:** use both the primary reasoning model for integration and
  correctness and the UI specialist for experience and visual quality.
- **Independent reviews:** choose the strongest suitable reviewer in fresh context;
  use a complementary model when a second perspective materially reduces risk.

Define a fallback for every mandatory specialist. When a preferred model or harness
is unavailable, use the strongest available model that meets the quality floor and
report the deviation when it affects confidence.

Keep authority in the primary parent model. Delegates investigate, advise, implement,
or review; the parent resolves disagreements, verifies the result, and owns the
user-facing answer.

## Delegation rules

Delegate when specialization, independent context, parallelism, or a separate review
materially improves the result—not as a ritual.

- Use role-shaped delegates such as `scout`, `researcher`, `planner`, `worker`,
  `reviewer`, and `oracle`.
- Parallelize independent, read-only reconnaissance, research, review, and validation.
- Keep **one writer per active worktree**. Use isolated worktrees only when parallel
  writers are genuinely necessary.
- Use fresh context for independent or adversarial review.
- Use inherited/forked context when a worker or adviser must understand decisions
  already made by the parent.
- Launch background work only when useful parent work can continue independently.
  Otherwise wait using the orchestration tool available in your environment.
- Do not let ordinary child agents recursively orchestrate more children unless they
  were explicitly assigned a bounded fan-out role.

### Herdr-managed delegation

If Herdr is installed **and the parent agent is running inside a Herdr-managed
pane** (`HERDR_ENV=1`), load and follow the installed
`herdr` skill when spawning subagents. Prefer named sibling panes so users can see,
inspect, focus, interrupt, and manage each delegate and its lifecycle status.

- Confirm both `HERDR_ENV=1` and that `herdr` is available before using it.
- Treat the installed CLI and `herdr --help` as the authority for current syntax.
- Preserve the caller's working directory and use background/no-focus pane creation
  unless the user requested another topology.
- Start the supported agent in the returned pane, assign a useful unique name, and
  submit the same compact child contract used by other delegation paths.
- Use Herdr's agent surface to prompt, wait, inspect state/output, and send interactive
  controls. Parse pane and agent identifiers from command responses rather than
  guessing them.
- Do not inspect or control a focused Herdr session from outside Herdr, and do not
  close panes, tabs, or workspaces you did not create without explicit permission.
- If Herdr is unavailable or Pi is not running inside it, fall back to the configured
  subagent/orchestration tool rather than trying to control Herdr externally.

Give every child a compact contract containing:

1. Goal and relevant evidence or files.
2. Approved scope and hard constraints.
3. Acceptance criteria.
4. Required validation.
5. Expected output or artifact.
6. Stop/escalation conditions.

## Substantial-change workflow

Scale this workflow to risk; do not turn tiny changes into ceremony.

1. **Clarify** material ambiguity.
2. **Define validation** and acceptance criteria.
3. **Investigate and plan** using read-only parallel work where useful.
4. Assign **one writer** to the active worktree.
5. Run **fresh, independent reviews** in parallel where risk warrants it.
6. Have the parent or designated writer resolve findings.
7. Perform **final parent verification**: diagnostics, tests, diff review, and
   residual-risk assessment.

A useful shorthand is:

```text
clarify → validation contract → plan → one writer
        → fresh reviews → fixes → final parent verification
```

## Optional external CLI delegates

An external agent CLI can be used as a bounded subagent when its harness or model is
useful. The parent remains responsible for scope, permissions, review, and validation.

Use a self-contained prompt containing the compact child contract. Prefer structured,
machine-readable output when the CLI supports it, retain raw run artifacts for
inspection, and verify both the process exit status and terminal result event.

General safety rules:

- Use read-only permissions for investigation, planning, and review.
- Grant write permission only to the designated writer in a trusted checkout.
- Allow only the build/test command patterns required by the task.
- Never bypass permission checks merely to make a blocked command succeed.
- Use a disposable sandbox or isolated worktree for intentionally risky operations.
- Pin budgets or turn limits for costly or open-ended assignments.
- Verify CLI flags against the installed version; agent CLIs evolve quickly.

Example shell shape—adapt flags to your CLI:

```bash
set -o pipefail
run_dir="$(mktemp -d "${TMPDIR:-/tmp}/agent-subtask.XXXXXX")"
cat >"$run_dir/prompt.md" <<'PROMPT'
<self-contained delegated task>
PROMPT

(
  cd "<target-cwd>"
  <agent-cli> <non-interactive-and-structured-output-flags> \
    -- "$(cat "$run_dir/prompt.md")"
) | tee "$run_dir/events.jsonl"
agent_status="${PIPESTATUS[0]}"
```

Afterward, inspect `agent_status`, parse the CLI's authoritative final event, review
changed files, and independently run or confirm validation.

## Direct CLI fallback

If the preferred orchestration extension is unavailable, a non-interactive coding
agent CLI can provide process isolation. Keep the task self-contained, restrict tools
for read-only work, use explicit provider/model selection where supported, and avoid
loading repository context only when the task is intentionally independent of it.
