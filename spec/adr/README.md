# Architecture Decision Records

Decisions are recorded as lightweight ADRs following the [archgate/cli](https://github.com/archgate/cli) format.

| ADR | Title | Status |
|-----|-------|--------|
| [001](001-pipeline-runner-as-separate-module.md) | Pipeline runner as a separate tools module | Accepted |
| [002](002-steps-as-plain-functions.md) | Steps as plain functions with decorator protocol | Accepted |
| [003](003-declarative-yaml-pipelines.md) | Declarative YAML pipeline definitions | Accepted |
| [004](004-docker-first-execution.md) | Docker-first execution with host fallback | Accepted |
| [005](005-structured-step-observability.md) | Structured logging and step-level observability | Accepted |

## Adding a new ADR

1. Copy an existing ADR as a template.
2. Number sequentially: `NNN-short-title.md`.
3. Status: `Proposed` → `Accepted` → `Superseded` (if replaced).
4. Update this README table.
