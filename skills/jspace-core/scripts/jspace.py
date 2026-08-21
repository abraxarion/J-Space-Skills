#!/usr/bin/env python3
"""Dependency-free epistemic state controller for J-Space Claude Code workflows."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

STATE_VERSION = 1
STATE_DIR = Path(".jspace")
STATE_FILE = STATE_DIR / "state.json"
STAGES = ("spec", "plan", "implement", "complete")
ARTIFACT_KINDS = ("spec", "plan", "implementation", "verification")
DOUBT_SEVERITIES = ("critical", "major", "minor")
DOUBT_STATUSES = ("open", "resolved", "accepted_risk", "deferred", "rejected")
EVIDENCE_KINDS = ("code", "test", "command", "document", "external", "observation")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def nonempty(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{label} must not be empty")
    return value


def new_state(title: str, goal: str) -> dict[str, Any]:
    now = utc_now()
    return {
        "schema_version": STATE_VERSION,
        "workflow_id": str(uuid.uuid4()),
        "title": nonempty(title, "title"),
        "stage": "spec",
        "goal": nonempty(goal, "goal"),
        "core_constraints": [],
        "artifacts": [],
        "doubts": [],
        "evidence": [],
        "decisions": [],
        "approvals": [],
        "reviews": [],
        "next": "Create and doubt-review the specification",
        "created_at": now,
        "updated_at": now,
    }


def save_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = utc_now()
    fd, temp_name = tempfile.mkstemp(prefix="state-", suffix=".json.tmp", dir=STATE_DIR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, STATE_FILE)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        raise FileNotFoundError("No .jspace/state.json found; run 'jspace init' first")
    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    if state.get("schema_version") != STATE_VERSION:
        raise ValueError(f"Unsupported state schema: {state.get('schema_version')!r}")
    return state


def next_id(prefix: str, items: Iterable[dict[str, Any]]) -> str:
    largest = 0
    for item in items:
        item_id = str(item.get("id", ""))
        if item_id.startswith(prefix + "-"):
            try:
                largest = max(largest, int(item_id.split("-", 1)[1]))
            except ValueError:
                pass
    return f"{prefix}-{largest + 1:03d}"


def find_id(items: Iterable[dict[str, Any]], item_id: str, label: str) -> dict[str, Any]:
    for item in items:
        if item.get("id") == item_id:
            return item
    raise ValueError(f"Unknown {label} id: {item_id}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_project_file(raw_path: str) -> tuple[str, Path]:
    root = Path.cwd().resolve()
    candidate = Path(raw_path)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Artifact path is outside project root: {raw_path}") from exc
    if not resolved.is_file():
        raise ValueError(f"Artifact file does not exist: {relative.as_posix()}")
    return relative.as_posix(), resolved


def latest_artifact(state: dict[str, Any], kind: str) -> dict[str, Any] | None:
    for artifact in reversed(state.get("artifacts", [])):
        if artifact.get("kind") == kind:
            return artifact
    return None


def artifact_hash_error(artifact: dict[str, Any]) -> str | None:
    try:
        relative, path = resolve_project_file(str(artifact["path"]))
    except ValueError as exc:
        return str(exc)
    if relative != artifact.get("path"):
        return f"Artifact path normalization changed for {artifact.get('id')}"
    current = sha256_file(path)
    if current != artifact.get("sha256"):
        return (
            f"Artifact {artifact.get('id')} hash is stale: registered "
            f"{artifact.get('sha256')}, current {current}"
        )
    return None


def current_approval(state: dict[str, Any], stage: str, artifact: dict[str, Any]) -> dict[str, Any] | None:
    for approval in reversed(state.get("approvals", [])):
        if (
            approval.get("stage") == stage
            and approval.get("artifact_id") == artifact.get("id")
            and approval.get("artifact_sha256") == artifact.get("sha256")
        ):
            return approval
    return None


def current_review(state: dict[str, Any], stage: str, artifact: dict[str, Any]) -> dict[str, Any] | None:
    for review in reversed(state.get("reviews", [])):
        if (
            review.get("stage") == stage
            and review.get("artifact_id") == artifact.get("id")
            and review.get("artifact_sha256") == artifact.get("sha256")
        ):
            return review
    return None


def relevant_doubt_blockers(state: dict[str, Any], stages: set[str]) -> list[str]:
    blockers: list[str] = []
    for doubt in state.get("doubts", []):
        if doubt.get("stage") not in stages:
            continue
        status = doubt.get("status")
        severity = doubt.get("severity")
        if status == "open" and severity == "critical":
            blockers.append(f"Critical doubt {doubt['id']} is still open: {doubt['claim']}")
        elif status == "open" and severity == "major":
            blockers.append(f"Major doubt {doubt['id']} lacks an explicit disposition: {doubt['claim']}")
        elif severity == "major" and status in {"resolved", "accepted_risk", "deferred"}:
            if not str(doubt.get("resolution", "")).strip():
                blockers.append(f"Major doubt {doubt['id']} has an empty disposition rationale")
    return blockers


def spec_gate_blockers(state: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    spec = latest_artifact(state, "spec")
    if spec is None:
        return ["No spec artifact is registered"]
    hash_error = artifact_hash_error(spec)
    if hash_error:
        blockers.append(hash_error)
    if current_review(state, "spec", spec) is None:
        blockers.append(f"No current skeptic review exists for spec {spec['id']} hash {spec['sha256']}")
    blockers.extend(relevant_doubt_blockers(state, {"spec"}))
    return blockers


def plan_gate_blockers(state: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    spec = latest_artifact(state, "spec")
    if spec is None:
        blockers.append("No spec artifact is registered")
    else:
        spec_hash_error = artifact_hash_error(spec)
        if spec_hash_error:
            blockers.append(f"Approved spec is stale: {spec_hash_error}")
        if current_approval(state, "spec", spec) is None:
            blockers.append(f"No current human approval exists for approved spec {spec['id']}")

    plan = latest_artifact(state, "plan")
    if plan is None:
        blockers.append("No plan artifact is registered")
    else:
        plan_hash_error = artifact_hash_error(plan)
        if plan_hash_error:
            blockers.append(plan_hash_error)
        if spec is not None and spec.get("id") not in plan.get("source_artifact_ids", []):
            blockers.append(f"Plan {plan['id']} does not reference approved spec {spec['id']} as a source")
        if current_review(state, "plan", plan) is None:
            blockers.append(f"No current skeptic review exists for plan {plan['id']} hash {plan['sha256']}")

    blockers.extend(relevant_doubt_blockers(state, {"spec", "plan"}))
    return blockers


def implement_gate_blockers(state: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    plan = latest_artifact(state, "plan")
    if plan is None:
        blockers.append("No plan artifact is registered")
    else:
        plan_hash_error = artifact_hash_error(plan)
        if plan_hash_error:
            blockers.append(f"Approved plan is stale: {plan_hash_error}")
        if current_approval(state, "plan", plan) is None:
            blockers.append(f"No current human approval exists for approved plan {plan['id']}")

    blockers.extend(relevant_doubt_blockers(state, {"spec", "plan", "implement"}))

    if not state.get("evidence"):
        blockers.append("No verification evidence is recorded")

    verification = latest_artifact(state, "verification")
    if verification is None:
        blockers.append("No verification artifact is registered")
    else:
        verification_error = artifact_hash_error(verification)
        if verification_error:
            blockers.append(f"Verification artifact is stale: {verification_error}")
    return blockers


def gate_blockers(state: dict[str, Any], stage: str) -> list[str]:
    if stage == "spec":
        return spec_gate_blockers(state)
    if stage == "plan":
        return plan_gate_blockers(state)
    if stage == "implement":
        return implement_gate_blockers(state)
    raise ValueError(f"Unknown gate stage: {stage}")


def open_doubt_counts(state: dict[str, Any]) -> dict[str, int]:
    counts = {"critical": 0, "major": 0, "minor": 0}
    for doubt in state.get("doubts", []):
        if doubt.get("status") == "open" and doubt.get("severity") in counts:
            counts[doubt["severity"]] += 1
    return counts


def command_init(args: argparse.Namespace) -> int:
    if STATE_FILE.exists() and not args.force:
        print("J-Space state already exists; use --force to replace it", file=os.sys.stderr)
        return 1
    save_state(new_state(args.title, args.goal))
    print(f"Initialized J-Space workflow: {args.title}")
    return 0


def command_status(args: argparse.Namespace) -> int:
    state = load_state()
    summary = {
        "workflow_id": state["workflow_id"],
        "title": state["title"],
        "stage": state["stage"],
        "goal": state["goal"],
        "open_doubts": open_doubt_counts(state),
        "artifacts": len(state.get("artifacts", [])),
        "evidence": len(state.get("evidence", [])),
        "next": state.get("next", ""),
    }
    if args.json:
        print(json.dumps(summary, sort_keys=True))
    else:
        print(f"Workflow: {summary['title']} ({summary['workflow_id']})")
        print(f"Stage: {summary['stage']}")
        print(f"Goal: {summary['goal']}")
        print(
            "Open doubts: "
            f"critical={summary['open_doubts']['critical']} "
            f"major={summary['open_doubts']['major']} "
            f"minor={summary['open_doubts']['minor']}"
        )
        print(f"Artifacts: {summary['artifacts']}  Evidence: {summary['evidence']}")
        print(f"Next: {summary['next']}")
    return 0


def command_artifact_register(args: argparse.Namespace) -> int:
    state = load_state()
    relative, path = resolve_project_file(args.path)
    for source_id in args.source:
        find_id(state["artifacts"], source_id, "artifact")
    artifact_id = next_id("A", state["artifacts"])
    artifact = {
        "id": artifact_id,
        "kind": args.kind,
        "path": relative,
        "sha256": sha256_file(path),
        "source_artifact_ids": list(args.source),
        "registered_at": utc_now(),
    }
    state["artifacts"].append(artifact)
    save_state(state)
    print(f"Registered {artifact_id} {args.kind} {relative}")
    return 0


def command_artifact_verify(args: argparse.Namespace) -> int:
    state = load_state()
    artifact = find_id(state["artifacts"], args.artifact_id, "artifact")
    error = artifact_hash_error(artifact)
    if error:
        print(f"Stale artifact: {error}", file=os.sys.stderr)
        return 2
    print(f"Artifact {artifact['id']} is current ({artifact['sha256']})")
    return 0


def command_doubt_add(args: argparse.Namespace) -> int:
    state = load_state()
    doubt_id = next_id("D", state["doubts"])
    doubt = {
        "id": doubt_id,
        "stage": args.stage,
        "claim": nonempty(args.claim, "claim"),
        "category": nonempty(args.category, "category"),
        "severity": args.severity,
        "status": "open",
        "evidence_for_ids": [],
        "evidence_against_ids": [],
        "resolution": "",
        "owner": args.owner.strip(),
        "created_at": utc_now(),
        "resolved_at": None,
    }
    state["doubts"].append(doubt)
    save_state(state)
    print(f"Added {doubt_id} {args.severity} {doubt['claim']}")
    return 0


def command_doubt_disposition(args: argparse.Namespace) -> int:
    state = load_state()
    doubt = find_id(state["doubts"], args.doubt_id, "doubt")
    if doubt.get("status") != "open":
        raise ValueError(f"Doubt {args.doubt_id} is already {doubt.get('status')}")
    resolution = nonempty(args.resolution, "resolution")
    doubt["status"] = args.disposition
    doubt["resolution"] = resolution
    doubt["resolved_at"] = utc_now()
    save_state(state)
    print(f"Disposition {args.doubt_id}: {args.disposition}")
    return 0


def command_evidence_add(args: argparse.Namespace) -> int:
    state = load_state()
    support_ids = list(args.supports)
    contradict_ids = list(args.contradicts)
    for doubt_id in support_ids + contradict_ids:
        find_id(state["doubts"], doubt_id, "doubt")
    evidence_id = next_id("E", state["evidence"])
    evidence = {
        "id": evidence_id,
        "kind": args.kind,
        "summary": nonempty(args.summary, "summary"),
        "locator": nonempty(args.locator, "locator"),
        "supports_doubt_ids": support_ids,
        "contradicts_doubt_ids": contradict_ids,
        "captured_at": utc_now(),
    }
    state["evidence"].append(evidence)
    for doubt_id in support_ids:
        doubt = find_id(state["doubts"], doubt_id, "doubt")
        if evidence_id not in doubt["evidence_for_ids"]:
            doubt["evidence_for_ids"].append(evidence_id)
    for doubt_id in contradict_ids:
        doubt = find_id(state["doubts"], doubt_id, "doubt")
        if evidence_id not in doubt["evidence_against_ids"]:
            doubt["evidence_against_ids"].append(evidence_id)
    save_state(state)
    print(f"Added {evidence_id} {args.kind} {evidence['summary']}")
    return 0


def command_review_record(args: argparse.Namespace) -> int:
    state = load_state()
    artifact = find_id(state["artifacts"], args.artifact_id, "artifact")
    expected_kind = args.stage
    if artifact.get("kind") != expected_kind:
        raise ValueError(f"{args.stage} review requires a {expected_kind} artifact")
    error = artifact_hash_error(artifact)
    if error:
        raise ValueError(f"Cannot record review for stale artifact: {error}")
    state["reviews"].append(
        {
            "stage": args.stage,
            "artifact_id": artifact["id"],
            "artifact_sha256": artifact["sha256"],
            "reviewer": nonempty(args.reviewer, "reviewer"),
            "reviewed_at": utc_now(),
        }
    )
    save_state(state)
    print(f"Recorded {args.stage} review for {artifact['id']} by {args.reviewer}")
    return 0


def command_approval_record(args: argparse.Namespace) -> int:
    state = load_state()
    artifact = find_id(state["artifacts"], args.artifact_id, "artifact")
    if artifact.get("kind") != args.stage:
        raise ValueError(f"{args.stage} approval requires a {args.stage} artifact")
    error = artifact_hash_error(artifact)
    if error:
        raise ValueError(f"Cannot approve stale artifact: {error}")
    blockers = gate_blockers(state, args.stage)
    if blockers:
        print("Approval blocked:")
        for blocker in blockers:
            print(f"- {blocker}")
        return 2
    state["approvals"].append(
        {
            "stage": args.stage,
            "artifact_id": artifact["id"],
            "approved_by": nonempty(args.approved_by, "approved by"),
            "approved_at": utc_now(),
            "artifact_sha256": artifact["sha256"],
        }
    )
    save_state(state)
    print(f"Recorded human approval for {args.stage} {artifact['id']}")
    return 0


def command_gate(args: argparse.Namespace) -> int:
    state = load_state()
    blockers = gate_blockers(state, args.stage)
    if blockers:
        print(f"{args.stage.capitalize()} gate BLOCKED")
        for blocker in blockers:
            print(f"- {blocker}")
        return 2
    print(f"{args.stage.capitalize()} gate PASSED")
    return 0


def command_stage_set(args: argparse.Namespace) -> int:
    state = load_state()
    current = state["stage"]
    target = args.stage
    if target == current:
        print(f"Stage already {target}")
        return 0
    if STAGES.index(target) < STAGES.index(current):
        raise ValueError(f"Cannot move workflow backward from {current} to {target}")
    expected_next = STAGES[STAGES.index(current) + 1] if current != "complete" else None
    if target != expected_next:
        raise ValueError(f"Stage transition must be sequential: {current} -> {expected_next}")

    if target == "plan":
        blockers = spec_gate_blockers(state)
        spec = latest_artifact(state, "spec")
        if not blockers and spec is not None and current_approval(state, "spec", spec) is None:
            blockers.append(f"No current human approval exists for spec {spec['id']}")
        if blockers:
            print("Stage transition BLOCKED")
            for blocker in blockers:
                print(f"- {blocker}")
            return 2
        state["next"] = "Create and doubt-review the implementation plan"
    elif target == "implement":
        blockers = plan_gate_blockers(state)
        plan = latest_artifact(state, "plan")
        if not blockers and plan is not None and current_approval(state, "plan", plan) is None:
            blockers.append(f"No current human approval exists for plan {plan['id']}")
        if blockers:
            print("Stage transition BLOCKED")
            for blocker in blockers:
                print(f"- {blocker}")
            return 2
        state["next"] = "Implement the approved plan and close implementation doubts"
    elif target == "complete":
        blockers = implement_gate_blockers(state)
        if blockers:
            print("Stage transition BLOCKED")
            for blocker in blockers:
                print(f"- {blocker}")
            return 2
        state["next"] = "Workflow complete"

    state["stage"] = target
    save_state(state)
    print(f"Stage set to {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jspace")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize workflow state")
    init_parser.add_argument("--title", required=True)
    init_parser.add_argument("--goal", required=True)
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=command_init)

    status_parser = subparsers.add_parser("status", help="show workflow status")
    status_parser.add_argument("--json", action="store_true")
    status_parser.set_defaults(func=command_status)

    artifact = subparsers.add_parser("artifact", help="register or verify artifacts")
    artifact_sub = artifact.add_subparsers(dest="artifact_command", required=True)
    artifact_register = artifact_sub.add_parser("register")
    artifact_register.add_argument("--kind", choices=ARTIFACT_KINDS, required=True)
    artifact_register.add_argument("--path", required=True)
    artifact_register.add_argument("--source", action="append", default=[])
    artifact_register.set_defaults(func=command_artifact_register)
    artifact_verify = artifact_sub.add_parser("verify")
    artifact_verify.add_argument("artifact_id")
    artifact_verify.set_defaults(func=command_artifact_verify)

    doubt = subparsers.add_parser("doubt", help="manage structured doubts")
    doubt_sub = doubt.add_subparsers(dest="doubt_command", required=True)
    doubt_add = doubt_sub.add_parser("add")
    doubt_add.add_argument("--stage", choices=("spec", "plan", "implement"), required=True)
    doubt_add.add_argument("--severity", choices=DOUBT_SEVERITIES, required=True)
    doubt_add.add_argument("--category", required=True)
    doubt_add.add_argument("--claim", required=True)
    doubt_add.add_argument("--owner", default="")
    doubt_add.set_defaults(func=command_doubt_add)
    for command_name, disposition in (
        ("resolve", "resolved"),
        ("accept-risk", "accepted_risk"),
        ("defer", "deferred"),
    ):
        disposition_parser = doubt_sub.add_parser(command_name)
        disposition_parser.add_argument("doubt_id")
        disposition_parser.add_argument("--resolution", required=True)
        disposition_parser.set_defaults(func=command_doubt_disposition, disposition=disposition)

    evidence = subparsers.add_parser("evidence", help="record evidence")
    evidence_sub = evidence.add_subparsers(dest="evidence_command", required=True)
    evidence_add = evidence_sub.add_parser("add")
    evidence_add.add_argument("--kind", choices=EVIDENCE_KINDS, required=True)
    evidence_add.add_argument("--summary", required=True)
    evidence_add.add_argument("--locator", required=True)
    evidence_add.add_argument("--supports", action="append", default=[])
    evidence_add.add_argument("--contradicts", action="append", default=[])
    evidence_add.set_defaults(func=command_evidence_add)

    review = subparsers.add_parser("review", help="record skeptic reviews")
    review_sub = review.add_subparsers(dest="review_command", required=True)
    review_record = review_sub.add_parser("record")
    review_record.add_argument("--stage", choices=("spec", "plan"), required=True)
    review_record.add_argument("--artifact-id", required=True)
    review_record.add_argument("--reviewer", required=True)
    review_record.set_defaults(func=command_review_record)

    approval = subparsers.add_parser("approval", help="record human approvals")
    approval_sub = approval.add_subparsers(dest="approval_command", required=True)
    approval_record = approval_sub.add_parser("record")
    approval_record.add_argument("--stage", choices=("spec", "plan"), required=True)
    approval_record.add_argument("--artifact-id", required=True)
    approval_record.add_argument("--by", dest="approved_by", required=True)
    approval_record.set_defaults(func=command_approval_record)

    gate = subparsers.add_parser("gate", help="evaluate artifact promotion gates")
    gate.add_argument("stage", choices=("spec", "plan", "implement"))
    gate.set_defaults(func=command_gate)

    stage = subparsers.add_parser("stage", help="advance workflow stage")
    stage_sub = stage.add_subparsers(dest="stage_command", required=True)
    stage_set = stage_sub.add_parser("set")
    stage_set.add_argument("stage", choices=STAGES)
    stage_set.set_defaults(func=command_stage_set)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
