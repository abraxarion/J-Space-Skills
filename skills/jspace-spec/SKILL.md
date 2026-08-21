---
name: jspace-spec
description: Create a Superpowers specification, then adversarially doubt-review and gate it before planning.
argument-hint: "<ticket, problem, or source material>"
disable-model-invocation: true
---

# J-Space Specification Workflow

Required dependency: obra/superpowers.

Do not reproduce Superpowers procedures. `superpowers:brainstorming` owns exploration, design, and specification creation. J-Space owns only explicit doubts, evidence, artifact identity, adversarial promotion review, and the promotion gate.

Before acting, read:

- `.claude/skills/jspace-core/references/superpowers-contract.md`
- `.claude/skills/jspace-core/references/doubt-protocol.md`
- `.claude/skills/jspace-core/references/artifact-gates.md`
- `.claude/skills/jspace-core/references/spec-skeptic.md`

Controller command prefix: `python .claude/skills/jspace-core/scripts/jspace.py`.

1. Run `python .claude/skills/jspace-core/scripts/jspace.py status --json`. If no workflow exists, initialize one from `$ARGUMENTS` with a concise title and goal. Never use `--force` unless the user explicitly asks to discard existing J-Space state.
2. Invoke `superpowers:brainstorming` and follow it exactly. Its design approval and written-spec user-review gates remain binding.
3. After the user has accepted the written Superpowers specification, register that exact file with `python .claude/skills/jspace-core/scripts/jspace.py artifact register --kind spec --path <path>`. The artifact is provisional until J-Space promotion completes.
4. Launch a **fresh Explore subagent** with the specification path, user goal, relevant repository constraints, and the full task protocol from `.claude/skills/jspace-core/references/spec-skeptic.md`. Use Explore because it is read-only. Do not ask the skeptic to rewrite files.
5. Evaluate the skeptic's candidate findings. Record material findings with `python .claude/skills/jspace-core/scripts/jspace.py doubt add ...`; record concrete supporting or contradicting evidence with `python .claude/skills/jspace-core/scripts/jspace.py evidence add ...`. Generic style preferences are not doubts.
6. Resolve critical/major doubts by gathering evidence, obtaining a binding user decision, or revising the specification through the owning Superpowers design/spec process. If the specification changes, register the changed artifact and run a fresh skeptic pass for its new hash.
7. When the skeptic pass for the current hash is complete, record it with `python .claude/skills/jspace-core/scripts/jspace.py review record --stage spec --artifact-id <current-id> --reviewer explore-spec-skeptic`.
8. Run `python .claude/skills/jspace-core/scripts/jspace.py gate spec`. If blocked, surface blockers and continue evidence/resolution work. Do not start planning.
9. When the gate passes, ask the user for final J-Space promotion approval of the current specification hash. After explicit approval, record it with `python .claude/skills/jspace-core/scripts/jspace.py approval record --stage spec --artifact-id <current-id> --by human`.
10. Stop. Planning begins only when the user invokes `/jspace-plan`.

Persist only concise doubt/evidence conclusions. Never persist chain-of-thought or model-introspection claims.
