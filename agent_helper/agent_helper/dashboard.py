"""Dashboard Docker container management."""

import subprocess
from pathlib import Path

from .config import get_data_dir, get_dashboard_port, get_repo_dir


def _docker_compose_file() -> Path:
    return get_repo_dir() / "docker-dashboard" / "docker-compose.yml"


def status() -> bool:
    """Check if the health-dashboard container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=health-dashboard", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return "health-dashboard" in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def start() -> bool:
    """Start the dashboard container via docker compose."""
    try:
        subprocess.run(
            ["docker", "compose", "-f", str(_docker_compose_file()), "up", "-d", "--build"],
            timeout=120,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Failed to start dashboard: {e}")
        return False


def stop() -> bool:
    """Stop the dashboard container."""
    try:
        subprocess.run(
            ["docker", "compose", "-f", str(_docker_compose_file()), "down"],
            timeout=30,
            check=False,
        )
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def info() -> dict:
    """Return dashboard status info."""
    running = status()
    port = get_dashboard_port()
    data_dir = get_data_dir()
    return {
        "running": running,
        "url": f"http://localhost:{port}" if running else None,
        "port": port,
        "data_dir": str(data_dir),
    }
