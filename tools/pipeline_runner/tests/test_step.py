"""Tests for the @step decorator."""

from pipeline_runner.errors import StepSkipped
from pipeline_runner.step import get_step_meta, step
from pipeline_runner.types import StepContext, StepResult


class TestStepDecorator:
    def test_basic_step_success(self, empty_context):
        @step("greet")
        def greet(ctx: StepContext) -> StepResult:
            return StepResult(status="success", step_name="greet", data={"msg": "hi"})

        result = greet(empty_context)
        assert result.status == "success"
        assert result.step_name == "greet"
        assert result.data == {"msg": "hi"}
        assert result.duration_seconds > 0

    def test_step_metadata(self):
        @step("my_step", description="Does things", retries=3, on_failure="continue")
        def my_step(ctx):
            return StepResult(status="success", step_name="my_step")

        meta = get_step_meta(my_step)
        assert meta is not None
        assert meta["name"] == "my_step"
        assert meta["description"] == "Does things"
        assert meta["retries"] == 3
        assert meta["on_failure"] == "continue"

    def test_step_handles_exception(self, empty_context):
        @step("failing")
        def failing(ctx):
            raise ValueError("something broke")

        result = failing(empty_context)
        assert result.status == "failed"
        assert "ValueError" in result.error
        assert "something broke" in result.error

    def test_step_skip(self, empty_context):
        @step("optional")
        def optional(ctx):
            raise StepSkipped("not needed today")

        result = optional(empty_context)
        assert result.status == "skipped"
        assert result.error == "not needed today"

    def test_step_retries(self, empty_context):
        call_count = 0

        @step("flaky", retries=2)
        def flaky(ctx):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("not yet")
            return StepResult(status="success", step_name="flaky")

        result = flaky(empty_context)
        assert result.status == "success"
        assert call_count == 3

    def test_step_retries_exhausted(self, empty_context):
        @step("always_fail", retries=1)
        def always_fail(ctx):
            raise RuntimeError("nope")

        result = always_fail(empty_context)
        assert result.status == "failed"
        assert "nope" in result.error

    def test_no_metadata_on_plain_function(self):
        def plain(ctx):
            pass

        assert get_step_meta(plain) is None
