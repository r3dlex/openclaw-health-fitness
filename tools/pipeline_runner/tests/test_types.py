"""Tests for core data types."""

import json

from pipeline_runner.types import PipelineResult, StepContext, StepResult


class TestStepContext:
    def test_defaults(self):
        ctx = StepContext()
        assert ctx.data == {}
        assert ctx.config == {}
        assert ctx.dry_run is False

    def test_get_set(self):
        ctx = StepContext()
        ctx.set("key", "value")
        assert ctx.get("key") == "value"
        assert ctx.get("missing", "default") == "default"

    def test_mutation_propagates(self):
        ctx = StepContext()
        ctx.set("step1", {"count": 5})
        assert ctx.data["step1"]["count"] == 5


class TestStepResult:
    def test_ok_on_success(self):
        r = StepResult(status="success", step_name="test")
        assert r.ok is True

    def test_ok_on_skipped(self):
        r = StepResult(status="skipped", step_name="test")
        assert r.ok is True

    def test_not_ok_on_failed(self):
        r = StepResult(status="failed", step_name="test", error="boom")
        assert r.ok is False

    def test_to_dict(self):
        r = StepResult(
            status="success",
            step_name="download",
            data={"path": "/tmp/file"},
            duration_seconds=1.234,
        )
        d = r.to_dict()
        assert d["status"] == "success"
        assert d["step_name"] == "download"
        assert d["data"]["path"] == "/tmp/file"
        assert d["duration_seconds"] == 1.234


class TestPipelineResult:
    def test_ok_on_success(self):
        r = PipelineResult(name="test", status="success")
        assert r.ok is True

    def test_ok_on_partial(self):
        r = PipelineResult(name="test", status="partial")
        assert r.ok is True

    def test_not_ok_on_failed(self):
        r = PipelineResult(name="test", status="failed")
        assert r.ok is False

    def test_failed_steps(self):
        r = PipelineResult(
            name="test",
            status="partial",
            steps=[
                StepResult(status="success", step_name="a"),
                StepResult(status="failed", step_name="b", error="err"),
                StepResult(status="success", step_name="c"),
            ],
        )
        assert len(r.failed_steps) == 1
        assert r.failed_steps[0].step_name == "b"

    def test_to_json(self):
        r = PipelineResult(name="test", status="success", duration_seconds=2.5)
        parsed = json.loads(r.to_json())
        assert parsed["name"] == "test"
        assert parsed["status"] == "success"
        assert parsed["duration_seconds"] == 2.5
