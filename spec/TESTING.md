# Testing

How to run tests, what's covered, and how to add new ones.

## Quick Start

```bash
# Pipeline runner tests (from repo root)
cd tools/pipeline_runner && poetry install --with dev && poetry run pytest

# With coverage
cd tools/pipeline_runner && poetry run pytest --cov=pipeline_runner --cov-report=term-missing

# Single test file
cd tools/pipeline_runner && poetry run pytest tests/test_step.py -v
```

Via Docker (zero-install):

```bash
docker build -t pipeline-runner-test -f tools/pipeline_runner/Dockerfile tools/pipeline_runner && \
docker run --rm pipeline-runner-test python -m pytest tests/ -v
```

## Test Structure

```
tools/pipeline_runner/tests/
  conftest.py              ← Shared fixtures (contexts, temp dirs)
  test_types.py            ← StepContext, StepResult, PipelineResult
  test_step.py             ← @step decorator, retries, skip, error handling
  test_pipeline.py         ← Pipeline orchestration, context propagation, failure modes
  test_loader.py           ← YAML loading, function resolution, validation
  test_runner.py           ← CLI commands (run, list, validate)
```

## What's Tested

### Unit Tests (no I/O)

| Module | Tests | What's Verified |
|--------|-------|-----------------|
| `types.py` | `test_types.py` | Dataclass defaults, serialization, `ok` property, `to_json()` |
| `step.py` | `test_step.py` | Decorator metadata, timing, retries, `StepSkipped`, exception handling |
| `pipeline.py` | `test_pipeline.py` | Sequential execution, context propagation, `on_failure: stop` vs `continue`, empty pipelines |
| `runner.py` | `test_runner.py` | CLI argument parsing, exit codes, JSON output |

### Integration Tests (filesystem)

| Module | Tests | What's Verified |
|--------|-------|-----------------|
| `loader.py` | `test_loader.py` | YAML parsing, function resolution, missing files, malformed YAML |

## Writing Tests

### Testing a Pipeline Step

Steps are plain functions — test them by constructing a context and calling directly:

```python
from pipeline_runner.types import StepContext, StepResult

def test_my_step():
    ctx = StepContext(config={"key": "value"})
    result = my_step(ctx)
    assert result.status == "success"
    assert result.data["count"] == 42
```

### Testing a Full Pipeline

```python
from pipeline_runner.pipeline import Pipeline
from pipeline_runner.types import StepContext

def test_my_pipeline():
    pipeline = Pipeline("test", steps=[step_a, step_b])
    result = pipeline.run(StepContext())
    assert result.ok
    assert len(result.steps) == 2
```

### Testing Step Error Handling

```python
from pipeline_runner.errors import StepSkipped

def test_step_skips_when_unconfigured(empty_context):
    result = optional_step(empty_context)
    assert result.status == "skipped"
```

## Fixtures

Defined in `tests/conftest.py`:

| Fixture | Description |
|---------|-------------|
| `empty_context` | Fresh `StepContext` with no data or config |
| `sample_context` | `StepContext` with typical config values |
| `dry_run_context` | `StepContext` with `dry_run=True` |

## Coverage Goals

- **Pipeline runner core**: 90%+ line coverage.
- **Bridge modules**: tested via integration tests when `agent_helper` is available.
- **All failure paths**: retries exhausted, YAML errors, missing functions, step exceptions.

## CI Integration

Tests run via `pytest` with no external dependencies. The pipeline runner has no runtime dependency on `agent_helper` — bridge modules use lazy imports (`from agent_helper.importers import ...` inside step functions) so the core engine is fully testable in isolation.

→ For pipeline concepts, see [spec/PIPELINES.md](PIPELINES.md).
→ For architecture decisions, see [spec/adr/](adr/).
