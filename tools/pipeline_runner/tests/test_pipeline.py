"""Tests for the Pipeline orchestrator."""

from pipeline_runner.pipeline import Pipeline
from pipeline_runner.step import step
from pipeline_runner.types import StepContext, StepResult


@step("step_a")
def step_a(ctx: StepContext) -> StepResult:
    ctx.set("step_a", {"value": 1})
    return StepResult(status="success", step_name="step_a", data={"value": 1})


@step("step_b")
def step_b(ctx: StepContext) -> StepResult:
    prev = ctx.get("step_a", {}).get("value", 0)
    return StepResult(status="success", step_name="step_b", data={"doubled": prev * 2})


@step("step_fail", on_failure="stop")
def step_fail(ctx: StepContext) -> StepResult:
    raise ValueError("intentional failure")


@step("step_fail_continue", on_failure="continue")
def step_fail_continue(ctx: StepContext) -> StepResult:
    raise ValueError("non-critical failure")


@step("step_c")
def step_c(ctx: StepContext) -> StepResult:
    return StepResult(status="success", step_name="step_c")


class TestPipeline:
    def test_empty_pipeline(self):
        p = Pipeline("empty")
        result = p.run(StepContext())
        assert result.status == "success"
        assert result.steps == []

    def test_success_pipeline(self):
        p = Pipeline("basic", steps=[step_a, step_b])
        result = p.run(StepContext())
        assert result.status == "success"
        assert len(result.steps) == 2
        assert result.steps[0].step_name == "step_a"
        assert result.steps[1].data["doubled"] == 2

    def test_context_propagation(self):
        ctx = StepContext()
        p = Pipeline("propagation", steps=[step_a, step_b])
        p.run(ctx)
        assert "step_a" in ctx.data

    def test_failure_stops_pipeline(self):
        p = Pipeline("stops", steps=[step_a, step_fail, step_c])
        result = p.run(StepContext())
        assert result.status == "failed"
        assert len(result.steps) == 2  # step_c never ran

    def test_failure_continue(self):
        p = Pipeline("continues", steps=[step_a, step_fail_continue, step_c])
        result = p.run(StepContext())
        assert result.status == "partial"
        assert len(result.steps) == 3  # all ran
        assert result.steps[1].status == "failed"
        assert result.steps[2].status == "success"

    def test_run_step_isolated(self):
        p = Pipeline("isolated")
        ctx = StepContext()
        result = p.run_step(step_a, ctx)
        assert result.status == "success"
        assert result.step_name == "step_a"

    def test_pipeline_duration(self):
        p = Pipeline("timed", steps=[step_a])
        result = p.run(StepContext())
        assert result.duration_seconds >= 0

    def test_add_step_chaining(self):
        p = Pipeline("chained")
        p.add_step(step_a).add_step(step_b)
        assert len(p.steps) == 2
