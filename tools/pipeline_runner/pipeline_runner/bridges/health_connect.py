"""Health Connect pipeline steps.

These steps wrap the existing agent_helper.importers functions,
adapting them to the pipeline runner's Step protocol.

Each step reads from ``ctx.config`` and writes results to ``ctx.data``.
"""

from __future__ import annotations

from pipeline_runner.errors import StepSkipped
from pipeline_runner.step import step
from pipeline_runner.types import StepContext, StepResult


@step("download", description="Download Health Connect ZIP from Google Drive mount", retries=1)
def download_step(ctx: StepContext) -> StepResult:
    """Locate and validate the Health Connect export ZIP."""
    from agent_helper.importers import download_health_connect

    source = ctx.config.get("health_connect_backup_dir", "")
    if not source:
        raise StepSkipped("HEALTH_CONNECT_BACKUP_DIR not configured")

    path = download_health_connect(source)
    return StepResult(
        status="success",
        step_name="download",
        data={"zip_path": str(path)},
    )


@step("extract", description="Extract SQLite database from ZIP archive")
def extract_step(ctx: StepContext) -> StepResult:
    """Extract the Health Connect SQLite DB from the downloaded ZIP."""
    from agent_helper.importers import extract_health_connect_db

    download_data = ctx.get("download", {})
    zip_path = download_data.get("zip_path") or ctx.config.get("zip_path")
    if not zip_path:
        raise StepSkipped("No ZIP path available from download step")

    db_path = extract_health_connect_db(zip_path)
    return StepResult(
        status="success",
        step_name="extract",
        data={"db_path": str(db_path)},
    )


@step("import_steps", description="Import step count data from SQLite to JSON")
def import_steps_step(ctx: StepContext) -> StepResult:
    """Import steps data from the extracted Health Connect DB."""
    from agent_helper.importers import import_steps

    extract_data = ctx.get("extract", {})
    db_path = extract_data.get("db_path") or ctx.config.get("db_path")
    if not db_path:
        raise StepSkipped("No DB path available from extract step")

    count = import_steps(db_path)
    return StepResult(
        status="success",
        step_name="import_steps",
        data={"records_imported": count},
    )


@step("import_sleep", description="Import sleep data from SQLite to JSON")
def import_sleep_step(ctx: StepContext) -> StepResult:
    """Import sleep data from the extracted Health Connect DB."""
    from agent_helper.importers import import_sleep

    extract_data = ctx.get("extract", {})
    db_path = extract_data.get("db_path") or ctx.config.get("db_path")
    if not db_path:
        raise StepSkipped("No DB path available from extract step")

    count = import_sleep(db_path)
    return StepResult(
        status="success",
        step_name="import_sleep",
        data={"records_imported": count},
    )


@step("dashboard_sync", description="Copy updated data files to dashboard container", on_failure="continue")
def dashboard_sync_step(ctx: StepContext) -> StepResult:
    """Sync JSON data files to the running dashboard container."""
    from agent_helper.importers import sync_to_dashboard

    synced = sync_to_dashboard()
    return StepResult(
        status="success",
        step_name="dashboard_sync",
        data={"files_synced": synced},
    )
