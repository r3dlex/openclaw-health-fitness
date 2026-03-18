# Pipelines

Step-based execution engine for health data workflows.

## Quick Start

```bash
# Run a pipeline
pipeline-runner run pipelines/health_connect_import.yaml

# List available pipelines
pipeline-runner list --dir pipelines/

# Validate without running
pipeline-runner validate pipelines/health_connect_import.yaml
```

Via Docker (zero-install):

```bash
python3 agent.py pipeline run health_connect_import
```

## Available Pipelines

| Pipeline | Steps | Description |
|----------|-------|-------------|
| `health_connect_import` | 5 | Download, extract, import steps+sleep, sync dashboard |

## How It Works

A **pipeline** is an ordered list of **steps**. Each step:
1. Receives a shared `StepContext` (config + accumulated data).
2. Does its work (download, transform, import, etc.).
3. Returns a `StepResult` with status, timing, and output data.

The pipeline runner executes steps sequentially, propagating results through the context so downstream steps can consume upstream output.

→ For architecture decisions behind this design, see [spec/adr/](adr/).

## Creating a Pipeline

Define steps in YAML:

```yaml
name: my-pipeline
description: What it does

steps:
  - name: first_step
    function: module.path:function_name
    description: What this step does

  - name: optional_step
    function: module.path:other_function
    on_failure: continue  # don't halt on failure
```

## Writing a Step

```python
from pipeline_runner import step, StepContext, StepResult

@step("my_step", description="Does a thing", retries=1)
def my_step(ctx: StepContext) -> StepResult:
    input_data = ctx.get("previous_step", {})
    # ... do work ...
    return StepResult(
        status="success",
        step_name="my_step",
        data={"records": 42},
    )
```

Steps are plain functions. The `@step` decorator adds:
- Automatic timing
- Retry logic (configurable)
- Exception → `StepResult` conversion
- Metadata for introspection

→ For testing steps, see [spec/TESTING.md](TESTING.md).

## Pipeline Results

Every run produces a JSON-serializable `PipelineResult`:

```json
{
  "name": "health-connect-import",
  "status": "success",
  "steps": [
    {"step_name": "download", "status": "success", "duration_seconds": 1.2},
    {"step_name": "import_steps", "status": "success", "data": {"records_imported": 56}}
  ],
  "duration_seconds": 4.8
}
```

Statuses: `success` (all passed), `partial` (some failed, pipeline continued), `failed` (critical step failed).

## Module Structure

```
tools/pipeline_runner/
  pipeline_runner/         ← Core engine (generic, no health knowledge)
    types.py               ← StepContext, StepResult, PipelineResult
    step.py                ← @step decorator
    pipeline.py            ← Pipeline orchestrator
    loader.py              ← YAML definition loader
    runner.py              ← CLI entry point
    bridges/               ← Domain-specific step implementations
      health_connect.py    ← Wraps agent_helper importers
  pipelines/               ← YAML pipeline definitions
  tests/                   ← Unit + integration tests
```

## CI

All pipeline YAML definitions are validated on every push. Pipeline runner tests run on Python 3.11–3.13 with an 80% coverage gate. See [spec/TESTING.md](TESTING.md) for details.

→ See [spec/ARCHITECTURE.md](ARCHITECTURE.md) for how pipelines fit into the system.
