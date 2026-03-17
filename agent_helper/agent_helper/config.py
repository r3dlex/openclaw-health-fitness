"""Environment and path configuration."""

import os
from pathlib import Path


def load_env(env_file: Path | None = None) -> None:
    """Load .env file into os.environ (without overriding existing vars)."""
    if env_file is None:
        # Walk up from this file to find .env
        candidate = Path(__file__).resolve().parent.parent.parent / ".env"
        if candidate.exists():
            env_file = candidate
    if env_file is None or not env_file.exists():
        return
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())


def get_data_dir() -> Path:
    """Return the data directory from HEALTH_FITNESS_DATA_FOLDER env var."""
    raw = os.environ.get("HEALTH_FITNESS_DATA_FOLDER")
    if not raw:
        raise EnvironmentError(
            "HEALTH_FITNESS_DATA_FOLDER is not set. "
            "Copy .env.example to .env and configure it."
        )
    path = Path(raw)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_repo_dir() -> Path:
    """Return the repository root directory.

    In Docker: /repo (mounted volume).
    Locally: two levels up from this file (agent_helper/agent_helper/config.py → repo root).
    """
    # Docker mounts the repo at /repo
    docker_repo = Path("/repo")
    if docker_repo.is_dir():
        return docker_repo
    return Path(__file__).resolve().parent.parent.parent


def get_reports_dir() -> Path:
    """Return the reports output directory."""
    d = get_repo_dir() / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_logs_dir() -> Path:
    """Return the logs directory."""
    d = get_repo_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_dashboard_port() -> str:
    """Return the dashboard port."""
    return os.environ.get("DASHBOARD_PORT", "8765")
