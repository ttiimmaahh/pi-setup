# Orchestration review rubric

Use this rubric to preserve the strengths of a sophisticated agent workflow while
removing accidental complexity and contradictions.

## Authority and responsibility

A strong policy names one parent/orchestrator that owns decomposition, model routing,
conflict resolution, final verification, and the user-facing answer. Subagents may
advise, investigate, implement, or review, but they do not silently redefine scope.

Check that delegation does not become responsibility laundering: the parent must
inspect evidence, resolve disagreements, and decide what ships.

## Role and model routing

Evaluate routing by capability and artifact:

- reasoning/architecture/debugging/correctness
- UI/UX/visual quality/accessibility/user-facing copy
- bounded implementation or mechanical execution
- lower-risk editorial work
- independent/adversarial review

A useful private policy can maintain a relative model matrix with cost, intelligence,
and taste scores. Cost should reflect the user's effective provider/harness economics;
intelligence estimates unsupervised problem difficulty and correctness; taste covers
UI/UX, API design, code quality, and prose. These are local decision aids, not
objective benchmarks.

During review, offer three paths: adopt the example matrix, customize it, or use
capability roles without numeric scores. When customizing, establish for each model:

- alias, provider, invocation harness, and availability
- relative cost, intelligence, and taste where useful
- preferred and explicitly excluded roles
- effort and context defaults
- fallback and escalation model

Also identify the primary orchestrator and suitable independent reviewers. Do not
invent scores for the user or require an axis that does not help their decisions.

A selection policy should classify task/artifact and risk, establish a minimum
intelligence floor, use taste for user-facing work, and compare cost only among models
that satisfy the quality requirement. It should account for harness/tool availability
and context independence, then define escalation when output misses the bar.
Correctness should outrank taste and cost for shipped work.

Local aliases and rankings are valid when they reflect configured models. A public
example may include an explicitly opinionated worked matrix, but users must replace
unavailable aliases and treat scores as editable. Every routing alias should map to a
matrix row or capability definition, and every mandatory specialist needs a fallback.

Flag absolute rules with no fallback, unavailable names, stale CLI flags, roles that
contradict scores without explanation, cost choices below the quality floor, or models
introduced only for variety. Important UI work should cover both experience/visual
quality and integration/correctness, whether through one qualified model or
complementary reviewers.

## Delegation shape

Strong delegation is role-shaped and bounded:

- Scouts/researchers gather evidence without writing.
- Planners turn evidence and constraints into an executable plan.
- One writer owns changes in an active worktree.
- Reviewers use fresh context when independence matters.
- Advisers/oracles inherit context only when accumulated decisions are necessary.

Parallelize independent read-only work. Parallel writers require intentionally
isolated worktrees and an explicit integration owner. Children should not recursively
spawn agents unless assigned a bounded fan-out role.

Each child contract should include goal, evidence/files, scope, constraints,
acceptance criteria, validation, expected output, and stop/escalation conditions.

## Context choice

Fresh context reduces confirmation bias and is preferred for adversarial reviews.
Forked/inherited context is appropriate when the child must understand prior decisions
or perform a tightly scoped continuation. Flag reviews described as independent when
they inherit the full parent transcript without justification.

## Herdr-aware operation

When Herdr is installed and the parent is actually inside it (`HERDR_ENV=1`), the
policy may require loading the `herdr` skill and using named sibling panes so the user
can observe and manage delegates. The guidance should preserve the caller's cwd and
focus, use returned pane/agent identifiers, and manage work through Herdr's lifecycle
surface.

Do not require Herdr when it is unavailable, and never direct an outside process to
control a focused Herdr session. Define a normal subagent fallback.

## Execution lifecycle

For substantial work, look for a scalable flow such as:

```text
clarify → validation contract → plan → one writer
        → fresh reviews → fixes → final parent verification
```

This is a default proportional to risk, not ceremony for tiny tasks. Background work
should be asynchronous only when the parent can continue useful independent work.

## Permissions and external CLIs

External CLIs remain bounded delegates. Check for:

- read-only permissions for investigation and review
- write access only for the designated writer
- narrowly allowed test/build commands
- no permission bypass merely to force success
- disposable worktrees/sandboxes for intentional risk
- turn/cost limits for open-ended work
- authoritative exit/result inspection and retained artifacts
- parent inspection of changed files and independent validation

Version-sensitive command flags should be verified against the installed CLI rather
than treated as timeless facts.

## Completion and evidence

“Done” should require evidence appropriate to the change: diagnostics before broad
builds where available, relevant tests, complete diff inspection, no silently skipped
checks, and a residual-risk statement. Failed or partial work must remain visibly
incomplete.

## Warning signs

- Multiple agents can write the same worktree concurrently.
- The reviewer is the writer with no independent pass on risky changes.
- Delegation is mandatory for trivial work or used without a concrete role.
- Conflicting model policies appear in different sections.
- A public template assumes private aliases, files, paths, or providers.
- Tool-specific instructions dominate global context despite rare use.
- Child results are accepted without parent verification.
- “Tests pass” is allowed when tests were skipped or validation failed.
