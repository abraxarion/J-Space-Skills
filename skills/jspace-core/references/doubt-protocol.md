# Doubt Protocol

## Purpose

A doubt is a compact, testable statement about something that may make an artifact wrong. It is not a transcript of internal reasoning.

Persist conclusions, evidence locators, and dispositions only. Never persist hidden chain-of-thought, scratch reasoning, or claims of privileged access to model internals.

## Candidate doubt fields

- `claim`: the assumption, ambiguity, contradiction, or risk being challenged;
- `category`: e.g. assumption, ambiguity, compatibility, dependency, coverage, migration, security, regression;
- `severity`: `critical`, `major`, or `minor`;
- `evidence_for`: concrete repository/document/test locators that support the challenged claim;
- `evidence_against`: concrete locators that contradict it;
- `recommended_resolution_test`: the smallest observation, inspection, experiment, or user decision that could settle it.

The skeptic agent returns candidate doubts. The coordinating Claude instance decides which findings are real enough to record with `python .claude/skills/jspace-core/scripts/jspace.py doubt add`.

## Severity

**Critical** — if wrong, the current artifact cannot safely be promoted. Examples: impossible requirement, wrong external contract, destructive migration assumption, security-critical uncertainty.

**Major** — materially affects architecture, scope, compatibility, correctness, or testability but may be explicitly resolved, accepted as risk, or deferred with rationale.

**Minor** — useful improvement or low-impact uncertainty. Minor doubts do not block promotion.

## Evidence

Prefer evidence in this order when applicable:

1. current repository code/configuration;
2. executable tests or commands;
3. authoritative project documentation/specification;
4. primary external documentation;
5. direct user decision for product/business ambiguity.

Do not promote “Claude thinks so” to evidence.

Record evidence with `python .claude/skills/jspace-core/scripts/jspace.py evidence add`. `locator` should let a later session find the evidence without reconstructing the entire conversation: file and line/symbol, command, test name, document section, or source URL/title.

## Dispositions

- `resolved`: evidence or a binding decision settles the doubt;
- `accepted_risk`: uncertainty remains but the human/project explicitly accepts the risk;
- `deferred`: intentionally postponed with a concrete rationale/scope boundary;
- `open`: unresolved;
- `rejected`: reserved in the state schema for future tooling; current CLI does not transition to it.

Every `resolved`, `accepted_risk`, or `deferred` major doubt requires non-empty resolution text.

## Re-review rule

Reviews are hash-bound. If the artifact changes after skeptic review, register the changed artifact as the current artifact and run a new skeptic review. Do not reuse the old marker as proof that the new content was reviewed.
