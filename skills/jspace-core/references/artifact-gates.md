# Artifact Gates

The Python controller performs deterministic checks only. It does not decide whether prose or code is correct.

## Specification

Typical sequence:

```text
python .claude/skills/jspace-core/scripts/jspace.py init --title "..." --goal "..."
python .claude/skills/jspace-core/scripts/jspace.py artifact register --kind spec --path <spec>
# run Explore subagent using `jspace-core/references/spec-skeptic.md` and record material doubts/evidence
python .claude/skills/jspace-core/scripts/jspace.py review record --stage spec --artifact-id <A-ID> --reviewer explore-spec-skeptic
python .claude/skills/jspace-core/scripts/jspace.py gate spec
# after explicit human promotion approval:
python .claude/skills/jspace-core/scripts/jspace.py approval record --stage spec --artifact-id <A-ID> --by human
python .claude/skills/jspace-core/scripts/jspace.py stage set plan
```

The spec gate requires a current spec hash, a skeptic review marker for that exact hash, no open critical spec doubt, and no open major spec doubt.

## Plan

```text
python .claude/skills/jspace-core/scripts/jspace.py artifact register --kind plan --path <plan> --source <SPEC-A-ID>
# run Explore subagent using `jspace-core/references/plan-skeptic.md` and record material doubts/evidence
python .claude/skills/jspace-core/scripts/jspace.py review record --stage plan --artifact-id <PLAN-A-ID> --reviewer explore-plan-skeptic
python .claude/skills/jspace-core/scripts/jspace.py gate plan
# after explicit human promotion approval:
python .claude/skills/jspace-core/scripts/jspace.py approval record --stage plan --artifact-id <PLAN-A-ID> --by human
python .claude/skills/jspace-core/scripts/jspace.py stage set implement
```

The plan gate additionally requires a current human-approved spec and the plan's source relation to that spec.

## Implementation

Use Superpowers for implementation and its normal reviews/verification. Before branch completion, record concrete evidence and a compact verification artifact:

```text
python .claude/skills/jspace-core/scripts/jspace.py evidence add --kind test --summary "..." --locator "<command/test>"
python .claude/skills/jspace-core/scripts/jspace.py artifact register --kind verification --path .jspace/verification.md
python .claude/skills/jspace-core/scripts/jspace.py gate implement
```

The implementation gate requires a current human-approved plan, explicit disposition of blocking doubts, at least one evidence record, and a current verification artifact.

Only after the implementation gate passes may the workflow proceed to `superpowers:finishing-a-development-branch`.

## Return codes

- `0`: passed/success;
- `1`: malformed command/state/input;
- `2`: a deterministic workflow gate or state transition is blocked.
