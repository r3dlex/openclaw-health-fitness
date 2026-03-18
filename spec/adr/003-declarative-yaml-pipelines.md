# ADR-003: Declarative YAML pipeline definitions

**Status:** Accepted

## Context

Pipelines need to be composable and inspectable without reading Python code. Non-developers (and the OpenClaw agent) should be able to understand and modify pipeline definitions.

## Decision

Pipelines can be defined in YAML files stored in `pipelines/`. The YAML schema specifies: name, description, and an ordered list of steps. Each step references a Python function via `module.path:function_name` notation.

The loader (`loader.py`) validates YAML at load time and resolves all function references before execution begins. Python-defined pipelines remain available for complex conditional logic.

## Consequences

- **Readable**: pipeline structure visible without running code.
- **Validated early**: bad references fail at load, not mid-execution.
- **CLI integration**: `pipeline-runner list`, `validate`, `run` all work with YAML.
- **Extensible**: new pipelines = new YAML files, no code changes needed for simple flows.
