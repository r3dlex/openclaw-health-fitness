#!/usr/bin/env python3
"""
OpenClaw Health Fitness Agent — entry point.
Delegates all work to the agent_helper module.

Docker (zero-install): auto-builds agent-helper image on first run.
Fallback: imports agent_helper directly if Docker unavailable.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
IMAGE = "agent-helper:latest"

# Env vars to forward into the Docker container (beyond the always-set ones).
_ENV_FORWARD = [
    "ZEPP_USER", "ZEPP_PASSWORD",
    "GOOGLE_DRIVE_EMAIL", "HEALTH_CONNECT_BACKUP_DIR",
    "TZ",
]


def _load_env():
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _ensure_image():
    check = subprocess.run(["docker", "image", "inspect", IMAGE], capture_output=True)
    if check.returncode == 0:
        return True
    print("Building agent-helper image...")
    build = subprocess.run(["docker", "build", "-t", IMAGE, str(ROOT / "agent_helper")])
    return build.returncode == 0


def _run_docker(args):
    data = os.environ.get("HEALTH_FITNESS_DATA_FOLDER", str(ROOT / "data"))
    port = os.environ.get("DASHBOARD_PORT", "8765")
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{data}:/data",
        "-v", f"{ROOT}:/repo",
        "-e", "HEALTH_FITNESS_DATA_FOLDER=/data",
        "-e", f"DASHBOARD_PORT={port}",
        "--network", "host",
    ]
    # Forward all configured env vars into the container
    for key in _ENV_FORWARD:
        val = os.environ.get(key)
        if val:
            cmd += ["-e", f"{key}={val}"]
    cmd.append(IMAGE)
    return subprocess.run(cmd + args).returncode


def _run_direct(args):
    sys.path.insert(0, str(ROOT / "agent_helper"))
    sys.argv = ["agent-helper"] + args
    from agent_helper.cli import main
    main()


if __name__ == "__main__":
    _load_env()
    args = sys.argv[1:] or ["daily", "weekly", "dashboard-status"]

    try:
        if _ensure_image():
            for a in (args if not sys.argv[1:] else [args]):
                _run_docker(a if isinstance(a, list) else [a])
        else:
            raise FileNotFoundError
    except (FileNotFoundError, OSError):
        _run_direct(args)
