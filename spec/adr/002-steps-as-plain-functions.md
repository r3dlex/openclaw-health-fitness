# ADR-002: Steps as plain functions with decorator protocol

**Status:** Accepted

## Context

Pipeline steps need to be independently testable. Class-based approaches (e.g. `Step` base class with `run()` method) add ceremony without clear benefit for this use case.

## Decision

Each step is a plain function decorated with `@step(name, ...)`. The decorator:
- Registers metadata (name, description, retries, on_failure).
- Wraps execution with timing, retry logic, and error handling.
- Converts exceptions to `StepResult` objects.

Steps receive a `StepContext` and return a `StepResult`. No inheritance required.

## Consequences

- **Minimal ceremony**: any function can be a step.
- **Easy testing**: construct a `StepContext`, call the function, assert the `StepResult`.
- **Introspectable**: `get_step_meta(fn)` retrieves decorator metadata.
- **No implicit state**: all input via context, all output via result.
