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

Local model aliases and rankings are valid in a private file when they reflect models
that are actually configured. For a portable file, prefer role placeholders and
clearly marked customization points. A routing rule is useful only when it states why
the role benefits from that model or harness.

Flag absolute rules that have no fallback, unavailable model names, stale CLI flags,
or extra models introduced only for variety. Correctness should outrank taste and
cost for shipped work.

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
