"""Pipeline orchestrator — composes and executes steps."""

from __future__ import annotations

import time
from typing import Callable

from pipeline_runner.step import get_step_meta
from pipeline_runner.types import PipelineResult, StepContext, StepResult


class Pipeline:
    """A named sequence of steps executed against a shared context.

    Example::

        pipeline = Pipeline("my-pipeline")
        pipeline.add_step(download_step)
        pipeline.add_step(transform_step)
        result = pipeline.run(StepContext(config={"key": "value"}))
        assert result.ok
    """

    def __init__(self, name: str, steps: list[Callable] | None = None):
        self.name = name
        self._steps: list[Callable] = list(steps or [])

    def add_step(self, step_fn: Callable) -> "Pipeline":
        """Append a step function. Returns self for chaining."""
        self._steps.append(step_fn)
        return self

    @property
    def steps(self) -> list[Callable]:
        return list(self._steps)

    def run(self, ctx: StepContext) -> PipelineResult:
        """Execute all steps in order. Returns aggregate result."""
        results: list[StepResult] = []
        start = time.monotonic()
        has_failure = False

        for step_fn in self._steps:
            result = self.run_step(step_fn, ctx)
            results.append(result)

            # Propagate step output into context for downstream steps
            if result.ok and result.data:
                meta = get_step_meta(step_fn)
                key = meta["name"] if meta else step_fn.__name__
                ctx.set(key, result.data)

            if result.status == "failed":
                has_failure = True
                meta = get_step_meta(step_fn)
                on_failure = (meta or {}).get("on_failure", "stop")
                if on_failure == "stop":
                    break

        duration = time.monotonic() - start

        if not has_failure:
            status = "success"
        elif len(results) < len(self._steps) or all(
            r.status == "failed" for r in results
        ):
            status = "failed"
        else:
            status = "partial"

        return PipelineResult(
            name=self.name,
            status=status,
            steps=results,
            duration_seconds=duration,
        )

    def run_step(self, step_fn: Callable, ctx: StepContext) -> StepResult:
        """Execute a single step in isolation. Useful for testing."""
        meta = get_step_meta(step_fn)
        step_name = meta["name"] if meta else step_fn.__name__

        try:
            return step_fn(ctx)
        except Exception as exc:
            return StepResult(
                status="failed",
                step_name=step_name,
                error=f"{type(exc).__name__}: {exc}",
            )
