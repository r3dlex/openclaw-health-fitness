"""Data loading and manipulation utilities."""

import json
from pathlib import Path
from typing import Any


def load_json(filepath: Path) -> list | dict:
    """Load a JSON file, returning empty list on failure."""
    try:
        with open(filepath) as f:
            content = f.read()
            return json.loads(content) if content.strip() else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_json(filepath: Path, data: Any, indent: int = 2) -> None:
    """Save data to a JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=indent)


def load_config(data_dir: Path) -> dict:
    """Load user constraints from config.json."""
    config = load_json(data_dir / "config.json")
    if isinstance(config, dict):
        return config.get("user_constraints", {})
    return {}


def filter_by_date(records: list[dict], date_str: str, field: str = "timestamp") -> list[dict]:
    """Filter records whose date field starts with the given date string."""
    return [r for r in records if r.get(field, "").startswith(date_str)]
