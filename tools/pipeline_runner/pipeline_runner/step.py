"""Step decorator and protocol for pipeline steps."""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, Protocol

from pipeline_runner.errors import StepSkipped
from pipeline_runner.types import StepContext, StepResult


class StepFunc(Protocol):
    """Protocol for a callable pipeline step."""

    def __call__(self, ctx: StepContext) -> StepResult: ...


# Metadata attribute name attached to decorated functions
_STEP_META = "_pipeline_step_meta"


def step(
    name: str,
    *,
    description: str = "",
    retries: int = 0,
    on_failure: str = "stop",
) -> Callable:
    """Decorator that marks a function as a pipeline step.

    Args:
        name: Unique step identifier within a pipeline.
        description: Human-readable description for logs and docs.
        retries: Number of retry attempts on failure (0 = no retries).
        on_failure: ``"stop"`` to halt the pipeline or ``"continue"`` to proceed.

    The decorated function receives a ``StepContext`` and must return a
    ``StepResult``. The decorator adds timing, retry logic, and error
    handling automatically.

    Example::

        @step("download", retries=2, on_failure="stop")
        def download_data(ctx: StepContext) -> StepResult:
            path = ctx.config["source_path"]
            ctx.set("download", {"path": path})
            return StepResult(status="success", step_name="download")
    """

    def decorator(fn: Callable[..., StepResult]) -> Callable[..., StepResult]:
        @functools.wraps(fn)
        def wrapper(ctx: StepContext) -> StepResult:
            last_error: str | None = None
            attempts = retries + 1

            for attempt in range(1, attempts + 1):
                start = time.monotonic()
                try:
                    result = fn(ctx)
                    result.duration_seconds = time.monotonic() - start
                    result.step_name = name
                    return result
                except StepSkipped as exc:
                    return StepResult(
                        status="skipped",
                        step_name=name,
                        error=str(exc) if str(exc) else None,
                        duration_seconds=time.monotonic() - start,
                    )
                except Exception as exc:
                    last_error = f"{type(exc).__name__}: {exc}"
                    if attempt < attempts:
                        continue  # retry
                    return StepResult(
                        status="failed",
                        step_name=name,
                        error=last_error,
                        duration_seconds=time.monotonic() - start,
                    )

            # Should never reach here, but just in case
            return StepResult(status="failed", step_name=name, error=last_error or "unknown error")

        # Attach metadata for introspection
        setattr(
            wrapper,
            _STEP_META,
            {
                "name": name,
                "description": description,
                "retries": retries,
                "on_failure": on_failure,
            },
        )
        return wrapper

    return decorator


def get_step_meta(fn: Callable) -> dict[str, Any] | None:
    """Retrieve step metadata from a decorated function, or None."""
    return getattr(fn, _STEP_META, None)
