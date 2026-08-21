---
name: jspace-core
description: Internal support files for the project-local J-Space workflows. Do not invoke directly.
disable-model-invocation: true
user-invocable: false
---

# J-Space Core

Shared controller and reference material for `jspace-spec`, `jspace-plan`, `jspace-implement`, and `jspace-status`.

Runtime state belongs in the repository root at `.jspace/`; never store workflow state inside `.claude/skills/`.
