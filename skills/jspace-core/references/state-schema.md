# State Schema

State is project-local at `.jspace/state.json` and currently uses `schema_version: 1`.

```json
{
  "schema_version": 1,
  "workflow_id": "uuid",
  "title": "Ticket 123",
  "stage": "spec",
  "goal": "Desired outcome",
  "core_constraints": [],
  "artifacts": [],
  "doubts": [],
  "evidence": [],
  "decisions": [],
  "approvals": [],
  "reviews": [],
  "next": "...",
  "created_at": "UTC timestamp",
  "updated_at": "UTC timestamp"
}
```

## Artifact

```json
{
  "id": "A-001",
  "kind": "spec|plan|implementation|verification",
  "path": "project/relative/path",
  "sha256": "...",
  "source_artifact_ids": [],
  "registered_at": "..."
}
```

## Doubt

```json
{
  "id": "D-001",
  "stage": "spec|plan|implement",
  "claim": "...",
  "category": "...",
  "severity": "critical|major|minor",
  "status": "open|resolved|accepted_risk|deferred|rejected",
  "evidence_for_ids": [],
  "evidence_against_ids": [],
  "resolution": "",
  "owner": "",
  "created_at": "...",
  "resolved_at": null
}
```

## Evidence

Evidence stores a concise summary and a durable locator, not reasoning traces.

## Approval and review

Both store the artifact ID **and the SHA-256 observed at the time**. Editing the file after review/approval makes that marker stale for promotion purposes.
