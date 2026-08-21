---
name: jspace-implement
description: Execute an approved Superpowers plan while carrying explicit doubts into existing reviews and requiring epistemic closure before branch completion.
argument-hint: "<approved implementation plan path>"
disable-model-invocation: true
---

# J-Space Implementation Workflow

Required dependency: obra/superpowers.

Do not reproduce Superpowers procedures. Superpowers owns worktrees, task execution, TDD, debugging, review, verification, and branch completion. J-Space supplies compact epistemic constraints and a final promotion gate.

Before acting, read:

- `.claude/skills/jspace-core/references/superpowers-contract.md`
- `.claude/skills/jspace-core/references/doubt-protocol.md`
- `.claude/skills/jspace-core/references/artifact-gates.md`

Controller command prefix: `python .claude/skills/jspace-core/scripts/jspace.py`.

1. Require `$ARGUMENTS` to identify the current human-approved plan. Run `python .claude/skills/jspace-core/scripts/jspace.py stage set implement`; if blocked, report blockers and stop.
2. Read `.jspace/state.json` and construct a compact **Doubt Context** containing only relevant doubt IDs, claims, severities, dispositions, resolution summaries, and evidence locators. Do not include hidden reasoning.
3. If subagents are available, invoke `superpowers:subagent-driven-development`; otherwise invoke `superpowers:executing-plans`. Supply the approved plan/spec plus the Doubt Context as additional constraints. Do not change those skills' normal TDD, review, debugging, or verification procedures.
4. The Superpowers execution workflow should return control immediately before `superpowers:finishing-a-development-branch`. Its normal implementation, task reviews, final review, fixes, and verification must happen first.
5. Convert new material implementation uncertainty discovered by those reviews/verification into `implement`-stage doubts. Record concrete evidence with `python .claude/skills/jspace-core/scripts/jspace.py evidence add ...` and resolve or explicitly disposition critical/major doubts.
6. Create `.jspace/verification.md` containing concise evidence only: current commit, verification commands/tests, pass/fail summaries, relevant final-review outcome, and unresolved minor/accepted risks. Do not store chain-of-thought.
7. Register it with `python .claude/skills/jspace-core/scripts/jspace.py artifact register --kind verification --path .jspace/verification.md`.
8. Run `python .claude/skills/jspace-core/scripts/jspace.py gate implement`. If blocked, return to the owning Superpowers debugging/review/verification skill needed to resolve the blocker; do not complete the branch.
9. Only after the implementation gate passes, invoke `superpowers:finishing-a-development-branch` and follow it exactly.

J-Space never substitutes its own code reviewer for Superpowers. Its job is to make uncertainty and evidence explicit at the boundary where completion would otherwise be claimed.
