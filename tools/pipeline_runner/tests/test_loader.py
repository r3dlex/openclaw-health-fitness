"""Tests for YAML pipeline loader."""

from pathlib import Path

import pytest

from pipeline_runner.errors import PipelineError
from pipeline_runner.loader import _resolve_function, list_pipelines, load_pipeline


@pytest.fixture
def valid_yaml(tmp_path: Path) -> Path:
    """Create a valid pipeline YAML using inline test step functions."""
    yaml_content = """\
name: test-pipeline
description: A test pipeline
steps:
  - name: dummy
    function: pipeline_runner._test_steps:dummy_step
    description: A dummy step for testing
"""
    p = tmp_path / "test_pipeline.yaml"
    p.write_text(yaml_content)
    return p


@pytest.fixture
def invalid_yaml(tmp_path: Path) -> Path:
    p = tmp_path / "bad.yaml"
    p.write_text("name: bad\n")  # no steps
    return p


@pytest.fixture
def malformed_yaml(tmp_path: Path) -> Path:
    p = tmp_path / "malformed.yaml"
    p.write_text(":\n  bad: [yaml\n")
    return p


# Dummy step function that the loader resolves
def _dummy_step(ctx):
    from pipeline_runner.types import StepResult
    return StepResult(status="success", step_name="dummy")


class TestLoadPipeline:
    def test_load_valid(self, valid_yaml):
        p = load_pipeline(valid_yaml)
        assert p.name == "test-pipeline"
        assert len(p.steps) == 1

    def test_missing_file(self):
        with pytest.raises(PipelineError, match="not found"):
            load_pipeline("/nonexistent/pipeline.yaml")

    def test_no_steps(self, invalid_yaml):
        with pytest.raises(PipelineError, match="no steps"):
            load_pipeline(invalid_yaml)

    def test_malformed_yaml(self, malformed_yaml):
        with pytest.raises(PipelineError, match="Invalid YAML"):
            load_pipeline(malformed_yaml)


class TestResolveFunction:
    def test_resolve_valid(self):
        fn = _resolve_function("pipeline_runner._test_steps:dummy_step")
        assert callable(fn)

    def test_missing_colon(self):
        with pytest.raises(PipelineError, match="Expected"):
            _resolve_function("pipeline_runner.types")

    def test_missing_module(self):
        with pytest.raises(PipelineError, match="Cannot import"):
            _resolve_function("nonexistent.module:func")

    def test_missing_function(self):
        with pytest.raises(PipelineError, match="not found"):
            _resolve_function("pipeline_runner.types:nonexistent_func")


class TestListPipelines:
    def test_list_empty(self, tmp_path):
        result = list_pipelines(tmp_path)
        assert result == []

    def test_list_valid(self, valid_yaml):
        result = list_pipelines(valid_yaml.parent)
        assert len(result) == 1
        assert result[0]["name"] == "test-pipeline"
        assert result[0]["steps"] == 1
