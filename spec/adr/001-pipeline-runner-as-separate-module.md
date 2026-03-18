# ADR-001: Pipeline runner as a separate tools module

**Status:** Accepted

## Context

The repo has `agent_helper/` for health-data business logic (importers, reports, dashboard). Pipelines are orchestration — composing steps, handling failures, retrying — which is a separate concern from domain logic.

Mixing orchestration into `agent_helper` would couple it to a specific execution model and make the pipeline engine non-reusable.

## Decision

Create `tools/pipeline_runner/` as a standalone Poetry package. It is a generic step-execution engine with no knowledge of health data. Domain-specific step functions live in bridge modules that import from both `pipeline_runner` and `agent_helper`.

## Consequences

- **Clean separation**: pipeline logic is reusable across projects.
- **`agent_helper` stays focused**: no orchestration concerns leak in.
- **Bridge pattern**: `pipeline_runner.bridges.health_connect` connects the two.
- **Docker**: the pipeline runner gets its own Dockerfile, following the same pattern as `agent_helper/Dockerfile`.
