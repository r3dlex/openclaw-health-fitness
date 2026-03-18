"""Shared test fixtures for pipeline runner tests."""

from __future__ import annotations

import pytest

from pipeline_runner.types import StepContext


@pytest.fixture
def empty_context() -> StepContext:
    """A fresh StepContext with no data or config."""
    return StepContext()


@pytest.fixture
def sample_context() -> StepContext:
    """A StepContext pre-loaded with typical config values."""
    return StepContext(
        config={
            "data_dir": "/tmp/test-data",
            "health_connect_backup_dir": "/tmp/hc-backup",
        },
    )


@pytest.fixture
def dry_run_context() -> StepContext:
    """A StepContext in dry-run mode."""
    return StepContext(dry_run=True)
