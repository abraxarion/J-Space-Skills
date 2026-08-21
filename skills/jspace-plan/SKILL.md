---
name: jspace-plan
description: Create a Superpowers implementation plan, adversarially doubt-review it, and gate it before implementation.
argument-hint: "<approved specification path>"
disable-model-invocation: true
---

# J-Space Plan Workflow

Required dependency: obra/superpowers.

Do not reproduce Superpowers procedures. `superpowers:writing-plans` owns implementation-plan construction. J-Space adds falsification, evidence, artifact identity, and promotion gates.

Before acting, read:

- `.claude/skills/jspace-core/references/superpowers-contract.md`
- `.claude/skills/jspace-core/references/doubt-protocol.md`
- `.claude/skills/jspace-core/references/artifact-gates.md`
- `.claude/skills/jspace-core/references/plan-skeptic.md`

Controller command prefix: `python .claude/skills/jspace-core/scripts/jspace.py`.

1. Inspect J-Space state. Require a current human-approved specification. Run `python .claude/skills/jspace-core/scripts/jspace.py stage set plan`; if blocked, report the exact blockers and do not create a plan.
2. Invoke `superpowers:writing-plans` using the approved specification in `$ARGUMENTS`. Let Superpowers own task granularity, TDD steps, file/interface planning, and plan self-review.
3. At Superpowers' execution handoff, do **not** begin implementation. The generated plan is provisional until this J-Space stage completes.
4. Register the plan with `python .claude/skills/jspace-core/scripts/jspace.py artifact register --kind plan --path <plan> --source <approved-spec-artifact-id>`.
5. Launch a **fresh Explore subagent** with the approved specification path, plan path, relevant repository constraints, and the full task protocol from `.claude/skills/jspace-core/references/plan-skeptic.md`. The skeptic must falsify rather than rewrite.
6. Convert material findings into structured doubts/evidence. Resolve critical/major plan doubts by verifying repository facts, revising the plan through `superpowers:writing-plans`, or obtaining an explicit binding decision where appropriate.
7. Any plan edit changes the artifact hash: register the new plan artifact and run a fresh skeptic pass against that hash.
8. Record the completed current-hash review with `python .claude/skills/jspace-core/scripts/jspace.py review record --stage plan --artifact-id <current-id> --reviewer explore-plan-skeptic`.
9. Run `python .claude/skills/jspace-core/scripts/jspace.py gate plan`. If blocked, do not implement.
10. When the gate passes, ask for final human promotion approval. After explicit approval, run `python .claude/skills/jspace-core/scripts/jspace.py approval record --stage plan --artifact-id <current-id> --by human`.
11. Stop. Implementation begins only when the user invokes `/jspace-implement`.

Do not add another planning methodology, TDD checklist, worktree process, or code-review process here; those remain Superpowers-owned.
