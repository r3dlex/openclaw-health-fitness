"""Core data types for pipeline execution."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class StepContext:
    """Mutable state bag passed through pipeline steps.

    Attributes:
        data: Accumulated output from prior steps. Each step writes to
              ``data[step_name]`` so downstream steps can consume it.
        config: Read-only configuration (env vars, paths, flags).
        dry_run: When True, steps should validate but not mutate external state.
    """

    data: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    dry_run: bool = False

    def get(self, key: str, default: Any = None) -> Any:
        """Shortcut to read from data with a fallback."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Shortcut to write to data."""
        self.data[key] = value


@dataclass
class StepResult:
    """Outcome of a single step execution.

    Attributes:
        status: One of ``success``, ``skipped``, or ``failed``.
        step_name: The registered name of the step.
        data: Any data the step wants to surface (counts, paths, etc.).
        error: Error message if status is ``failed``.
        duration_seconds: Wall-clock time for the step.
    """

    status: Literal["success", "skipped", "failed"]
    step_name: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_seconds: float = 0.0

    @property
    def ok(self) -> bool:
        return self.status in ("success", "skipped")

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "step_name": self.step_name,
            "data": self.data,
            "error": self.error,
            "duration_seconds": round(self.duration_seconds, 3),
        }


@dataclass
class PipelineResult:
    """Aggregate outcome of a full pipeline run.

    Attributes:
        name: Pipeline name.
        status: ``success`` if all steps passed, ``partial`` if some failed
                but pipeline continued, ``failed`` if a critical step failed.
        steps: Ordered list of step results.
        duration_seconds: Total wall-clock time.
    """

    name: str
    status: Literal["success", "partial", "failed"]
    steps: list[StepResult] = field(default_factory=list)
    duration_seconds: float = 0.0

    @property
    def ok(self) -> bool:
        return self.status in ("success", "partial")

    @property
    def failed_steps(self) -> list[StepResult]:
        return [s for s in self.steps if s.status == "failed"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "duration_seconds": round(self.duration_seconds, 3),
        }

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), **kwargs)
