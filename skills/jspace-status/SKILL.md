---
name: jspace-status
description: Show the current J-Space workflow stage, doubts, artifacts, evidence, approvals, reviews, and deterministic blockers without mutating state.
disable-model-invocation: true
---

# J-Space Status

Controller command prefix: `python .claude/skills/jspace-core/scripts/jspace.py`.

Run `python .claude/skills/jspace-core/scripts/jspace.py status --json` and read `.jspace/state.json` only if more detail is needed. Summarize:

- current stage and goal;
- current spec/plan/verification artifact IDs and whether their files still match registered hashes;
- open critical/major/minor doubts;
- latest human approvals and skeptic reviews;
- the next expected action.

For the current stage, you may run `python .claude/skills/jspace-core/scripts/jspace.py gate <stage>` to show deterministic blockers. Do not mutate state and do not resolve doubts on the user's behalf.
