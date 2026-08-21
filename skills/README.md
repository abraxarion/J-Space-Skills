# J-Space Project Skills

This directory is the source for the direct-install, project-local skill bundle: the five `jspace-*` directories are copied directly into a target repository's `.claude/skills/` directory.

| Skill | Purpose |
|---|---|
| `jspace-spec` | Specification workflow with adversarial skeptic review and a promotion gate |
| `jspace-plan` | Implementation-plan workflow with adversarial skeptic review and a promotion gate |
| `jspace-implement` | Implementation with doubt context, verification evidence, and a final gate |
| `jspace-status` | Read-only workflow status and deterministic blockers |
| `jspace-core` | Shared controller (`scripts/jspace.py`) and reference protocols — never invoked directly |

## Requirements

- **Claude Code**
- **[`obra/superpowers`](https://github.com/obra/superpowers)** installed (hard dependency — the workflows stop with a clear error if it is missing)
- **Python 3** — the controller uses the standard library only

The workflows add token overhead — see the Costs section of the repository README for details.

## Installation

From this repository's root:

```bash
cp -r skills/jspace-* /path/to/your/repo/.claude/skills/
```

Runtime state is stored at the repository root in `.jspace/` — never inside `.claude/skills/`. Whether `.jspace/` is versioned is your call: add it to `.gitignore` to keep the workflow state local and per-developer, or commit it to share the audit trail of doubts, approvals, and gates with the team.

## Usage

```text
/jspace-spec <ticket or problem>          # spec + skeptic review + gate
/jspace-plan <approved spec path>         # plan + skeptic review + gate
/jspace-implement <approved plan path>    # implement + verify + gate
/jspace-status                            # read-only status and blockers
```

See the [repository README](../README.md) for the full workflow guide, gate conditions, and research references.
