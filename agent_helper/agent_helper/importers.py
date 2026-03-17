"""Data importers for Health Connect SQLite databases."""

import json
import os
import shutil
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from .config import get_data_dir, get_logs_dir
from .data import load_json, save_json


def _log(msg: str, log_file: Path | None = None) -> None:
    """Print a timestamped log message and optionally append to file."""
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a") as f:
            f.write(line + "\n")


def _epoch_days_to_date(days_str: str) -> str:
    """Convert Health Connect local_date (days since epoch) to YYYY-MM-DD."""
    try:
        days = int(days_str)
        if days > 10000:  # Looks like epoch days, not a year
            d = datetime(1970, 1, 1) + timedelta(days=days)
            return d.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        pass
    return str(days_str)


def import_steps(db_path: str | Path, output_path: str | Path | None = None) -> dict:
    """Import steps data from Health Connect SQLite into steps.json.

    Args:
        db_path: Path to Health Connect SQLite database.
        output_path: Path to steps.json. Defaults to $HEALTH_FITNESS_DATA_FOLDER/steps.json.

    Returns:
        Summary dict with counts.
    """
    if output_path is None:
        output_path = get_data_dir() / "steps.json"
    output_path = Path(output_path)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date(start_time/1000, 'unixepoch') AS day, SUM(count) AS steps
        FROM steps_record_table
        GROUP BY day
        ORDER BY day
    """)

    by_date = {}
    for row in cursor.fetchall():
        if row[0]:
            by_date[row[0]] = row[1]
    conn.close()

    # Merge with existing data
    existing = load_json(output_path)
    existing_by_date = existing.get("by_date", {}) if isinstance(existing, dict) else {}
    merged = {**existing_by_date, **by_date}

    steps_data = {
        "total_steps": sum(merged.values()),
        "by_date": dict(sorted(merged.items())),
        "last_updated": datetime.now().isoformat(),
        "source": "health_connect",
    }
    save_json(output_path, steps_data)

    # Sync to Docker if running
    subprocess.run(
        ["docker", "cp", str(output_path), "health-dashboard:/usr/share/nginx/html/data/steps.json"],
        capture_output=True,
    )

    return {"new_days": len(by_date), "total_days": len(merged), "total_steps": steps_data["total_steps"]}


def import_sleep(db_path: str | Path, output_path: str | Path | None = None) -> dict:
    """Import sleep data from Health Connect SQLite into sleep.json.

    Converts local_date from epoch-days to YYYY-MM-DD format.
    Deduplicates by keeping the longest sleep per date.

    Args:
        db_path: Path to Health Connect SQLite database.
        output_path: Path to sleep.json. Defaults to $HEALTH_FITNESS_DATA_FOLDER/sleep.json.

    Returns:
        Summary dict with counts.
    """
    if output_path is None:
        output_path = get_data_dir() / "sleep.json"
    output_path = Path(output_path)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            local_date,
            (end_time - start_time) / 1000 / 60 AS duration_minutes
        FROM sleep_session_record_table
        ORDER BY local_date DESC
    """)

    sleep_by_date: dict[str, dict] = {}
    for row in cursor.fetchall():
        raw_date, duration_min = row
        date_str = _epoch_days_to_date(str(raw_date))
        hours = duration_min / 60

        if date_str not in sleep_by_date or hours > sleep_by_date[date_str]["duration_hours"]:
            sleep_by_date[date_str] = {
                "date": date_str,
                "duration_hours": round(hours, 2),
                "duration_minutes": duration_min,
                "source": "health_connect",
            }
    conn.close()

    # Load existing, index health_connect entries
    existing = load_json(output_path)
    if not isinstance(existing, list):
        existing = []

    existing_hc_dates = {
        e["date"]: i for i, e in enumerate(existing) if e.get("source") == "health_connect"
    }

    for date_str, data in sleep_by_date.items():
        if date_str in existing_hc_dates:
            existing[existing_hc_dates[date_str]] = data
        else:
            existing.append(data)

    existing.sort(key=lambda x: x.get("date", ""))
    save_json(output_path, existing)

    return {"imported": len(sleep_by_date), "total": len(existing)}


def download_health_connect() -> Path | None:
    """Download Health Connect ZIP from Google Drive mount.

    Returns the path to the downloaded file, or None on failure.
    """
    google_email = os.environ.get("GOOGLE_DRIVE_EMAIL")
    if not google_email:
        print("ERROR: GOOGLE_DRIVE_EMAIL not set in .env")
        return None

    source = Path.home() / f"Library/CloudStorage/GoogleDrive-{google_email}/My Drive/health_connect_daily.zip"
    dest = Path("/tmp/health_connect_latest.zip")
    log_file = get_logs_dir() / "health_connect.log"

    if not source.exists():
        _log(f"ERROR: Not found: {source}", log_file)
        _log("Make sure Google Drive is mounted", log_file)
        return None

    _log(f"Found: {source}", log_file)
    dest.unlink(missing_ok=True)

    try:
        shutil.copy2(str(source), str(dest))
        _log("Downloaded successfully", log_file)
        return dest
    except OSError as e:
        _log(f"WARNING: Copy failed ({e}) - file may be locked", log_file)
        return None


def run_full_import() -> dict:
    """Run the complete Health Connect import pipeline.

    Downloads ZIP, extracts, imports steps + sleep.

    Returns:
        Summary dict with results from each stage.
    """
    log_file = get_logs_dir() / "health_connect.log"
    results: dict = {}

    # Download
    zip_path = download_health_connect()
    if zip_path is None:
        return {"error": "Download failed"}

    # Backup
    backup_dir = os.environ.get("HEALTH_CONNECT_BACKUP_DIR")
    if backup_dir:
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y_%m_%d")
        target = backup_path / f"health_connect_daily_{today}.zip"
        shutil.copy2(str(zip_path), str(target))
        _log(f"Backed up to {target}", log_file)

    # Extract
    temp_dir = Path("/tmp/health_connect_latest")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    _log("Extracting...", log_file)
    subprocess.run(["unzip", "-o", str(zip_path), "-d", str(temp_dir)], capture_output=True)

    db_file = temp_dir / "health_connect_export.db"
    if not db_file.exists():
        _log("ERROR: No database found in archive", log_file)
        return {"error": "No database in archive"}

    # Import
    _log("Importing steps...", log_file)
    results["steps"] = import_steps(db_file)

    _log("Importing sleep...", log_file)
    results["sleep"] = import_sleep(db_file)

    _log("Import complete", log_file)
    return results
