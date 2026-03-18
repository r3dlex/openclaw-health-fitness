"""Tests for the CLI runner."""

from pathlib import Path

import pytest

from pipeline_runner.runner import main


@pytest.fixture
def runnable_yaml(tmp_path: Path) -> Path:
    """Create a pipeline YAML that uses a resolvable step."""
    yaml_content = """\
name: cli-test
description: CLI test pipeline
steps:
  - name: noop
    function: pipeline_runner._test_steps:noop_step
"""
    p = tmp_path / "cli_test.yaml"
    p.write_text(yaml_content)
    return p


def _noop_step(ctx):
    from pipeline_runner.types import StepResult
    return StepResult(status="success", step_name="noop", data={"ran": True})


class TestCLI:
    def test_no_args(self):
        assert main([]) == 0

    def test_list_empty(self, tmp_path):
        assert main(["list", "--dir", str(tmp_path)]) == 0

    def test_list_with_pipelines(self, runnable_yaml):
        assert main(["list", "--dir", str(runnable_yaml.parent)]) == 0

    def test_validate_valid(self, runnable_yaml):
        assert main(["validate", str(runnable_yaml)]) == 0

    def test_validate_invalid(self):
        assert main(["validate", "/nonexistent.yaml"]) == 1

    def test_run_success(self, runnable_yaml, capsys):
        code = main(["run", str(runnable_yaml)])
        assert code == 0
        captured = capsys.readouterr()
        assert '"status": "success"' in captured.out

    def test_run_dry_run(self, runnable_yaml, capsys):
        code = main(["run", str(runnable_yaml), "--dry-run"])
        assert code == 0

    def test_run_with_config(self, runnable_yaml, capsys):
        code = main(["run", str(runnable_yaml), "--config", '{"key": "val"}'])
        assert code == 0

    def test_run_bad_config_json(self, runnable_yaml):
        code = main(["run", str(runnable_yaml), "--config", "not-json"])
        assert code == 1
