# Superpowers Contract

J-Space is an epistemic-control extension for repositories that already use obra/superpowers. It does **not** vendor, paraphrase, or replace Superpowers procedures.

## Ownership

| Engineering responsibility | Owner |
|---|---|
| Problem exploration, brainstorming, design, specification generation | `superpowers:brainstorming` |
| Detailed implementation-plan generation | `superpowers:writing-plans` |
| Workspace isolation | `superpowers:using-git-worktrees` |
| Same-session task execution with fresh subagents | `superpowers:subagent-driven-development` |
| Inline/separate-session plan execution | `superpowers:executing-plans` |
| Feature and bugfix coding discipline | `superpowers:test-driven-development` |
| Root-cause debugging | `superpowers:systematic-debugging` |
| Requesting code review | `superpowers:requesting-code-review` |
| Processing review feedback | `superpowers:receiving-code-review` |
| Evidence before completion claims | `superpowers:verification-before-completion` |
| Merge/PR/branch cleanup decisions | `superpowers:finishing-a-development-branch` |

## J-Space ownership

J-Space owns only:

1. explicit assumptions and doubts;
2. evidence references for or against those doubts;
3. adversarial falsification at spec and plan artifact boundaries;
4. hash-bound skeptic-review markers and human approvals;
5. deterministic promotion gates;
6. carrying compact doubt context into existing Superpowers implementation/review/verification work;
7. final epistemic closure before branch completion.

## No-copy rule

When a J-Space workflow reaches a responsibility in the ownership table, invoke the named Superpowers skill and follow it. Do not restate its checklist, simulate a substitute, or create a second implementation of the same methodology.

J-Space may add an **external boundary condition** around a Superpowers workflow. Example: Superpowers implementation/review runs normally, but `superpowers:finishing-a-development-branch` must not begin until the J-Space implementation gate has recorded verification evidence and passed.

## Dependency behavior

If obra/superpowers is unavailable, stop and report the missing dependency. Do not silently replace it with generic instructions.
