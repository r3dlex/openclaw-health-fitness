# ADR-004: Docker-first execution with host fallback

**Status:** Accepted

## Context

The repo follows a zero-install principle: `agent.py` builds Docker images on first use. Users need only Python 3 and Docker. This pattern must extend to the pipeline runner.

## Decision

The pipeline runner has its own `Dockerfile` following the same pattern as `agent_helper/Dockerfile`. `agent.py` gains a `pipeline` subcommand that builds and runs the pipeline runner container, mounting `$HEALTH_FITNESS_DATA_FOLDER` as `/data`.

For local development, `cd tools/pipeline_runner && poetry install && pipeline-runner run ...` works directly.

## Consequences

- **Consistent**: same Docker-first pattern across all components.
- **Zero-install**: users never run `pip install` manually.
- **Dev-friendly**: Poetry provides a direct execution path for testing.
