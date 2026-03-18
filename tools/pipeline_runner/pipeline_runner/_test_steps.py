"""Dummy step functions for testing. Part of the package so they're importable."""

from pipeline_runner.step import step
from pipeline_runner.types import StepContext, StepResult


@step("dummy", description="A dummy step for testing")
def dummy_step(ctx: StepContext) -> StepResult:
    return StepResult(status="success", step_name="dummy", data={"test": True})


@step("noop", description="No-op step for CLI testing")
def noop_step(ctx: StepContext) -> StepResult:
    return StepResult(status="success", step_name="noop", data={"ran": True})
