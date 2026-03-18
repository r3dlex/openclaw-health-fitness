# ADR-005: Structured logging and step-level observability

**Status:** Accepted

## Context

The existing import pipeline uses `print()` statements. Debugging failures requires reading terminal output. Pipeline runs need structured, machine-readable results for logging, dashboarding, and automated monitoring.

## Decision

Each step returns a `StepResult` with status, timing, data, and error fields. The `Pipeline.run()` method collects these into a `PipelineResult` which is JSON-serializable.

The CLI runner outputs `PipelineResult.to_json()` to stdout. Results can be stored in `logs/` for historical analysis.

## Consequences

- **Debuggable**: every step has clear status, timing, and error info.
- **Machine-readable**: JSON output integrates with monitoring tools.
- **Audit trail**: pipeline results can be persisted for trend analysis.
- **No external dependencies**: uses stdlib `json` and `dataclasses`.
