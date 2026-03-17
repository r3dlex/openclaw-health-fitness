"""CLI entry point for the agent-helper tool."""

import sys
from datetime import datetime

from .config import load_env


def main() -> None:
    """Main CLI dispatcher."""
    load_env()

    if len(sys.argv) < 2:
        _usage()
        return

    command = sys.argv[1]
    handlers = {
        "daily": _cmd_daily,
        "weekly": _cmd_weekly,
        "report": _cmd_report,
        "import": _cmd_import,
        "import-steps": _cmd_import_steps,
        "import-sleep": _cmd_import_sleep,
        "dashboard-status": _cmd_dashboard_status,
        "dashboard-start": _cmd_dashboard_start,
        "dashboard-stop": _cmd_dashboard_stop,
        "dashboard-info": _cmd_dashboard_info,
    }

    handler = handlers.get(command)
    if handler is None:
        print(f"Unknown command: {command}")
        _usage()
        sys.exit(1)

    handler()


def _usage() -> None:
    print("""Usage: agent-helper <command>

Commands:
  daily                Generate daily report
  weekly               Generate weekly report (Sundays only)
  report [YYYY-MM-DD]  Generate report for a specific date

  import               Run full Health Connect import pipeline
  import-steps <db>    Import steps from SQLite database
  import-sleep <db>    Import sleep from SQLite database

  dashboard-status     Check if dashboard is running
  dashboard-start      Start dashboard container
  dashboard-stop       Stop dashboard container
  dashboard-info       Show dashboard details""")


def _cmd_daily() -> None:
    from .reports import write_daily_report

    path = write_daily_report()
    print(f"  Daily report: {path}")


def _cmd_weekly() -> None:
    from .reports import write_weekly_report

    path = write_weekly_report()
    if path:
        print(f"  Weekly report: {path}")
    else:
        print("  Skipped (not Sunday)")


def _cmd_report() -> None:
    from .reports import generate_daily_report

    date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.now().isoformat()[:10]
    print(generate_daily_report(date_str))


def _cmd_import() -> None:
    from .importers import run_full_import

    results = run_full_import()
    if "error" in results:
        print(f"  Import failed: {results['error']}")
        sys.exit(1)
    print(f"  Steps: {results.get('steps', {})}")
    print(f"  Sleep: {results.get('sleep', {})}")


def _cmd_import_steps() -> None:
    from .importers import import_steps

    if len(sys.argv) < 3:
        print("Usage: agent-helper import-steps <db_path> [output_path]")
        sys.exit(1)
    db_path = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else None
    result = import_steps(db_path, output)
    print(f"  Steps imported: {result}")


def _cmd_import_sleep() -> None:
    from .importers import import_sleep

    if len(sys.argv) < 3:
        print("Usage: agent-helper import-sleep <db_path> [output_path]")
        sys.exit(1)
    db_path = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else None
    result = import_sleep(db_path, output)
    print(f"  Sleep imported: {result}")


def _cmd_dashboard_status() -> None:
    from .dashboard import status

    running = status()
    print(f"Dashboard running: {running}")


def _cmd_dashboard_start() -> None:
    from .dashboard import start

    if start():
        print("Dashboard started")
    else:
        print("Failed to start dashboard")
        sys.exit(1)


def _cmd_dashboard_stop() -> None:
    from .dashboard import stop

    stop()
    print("Dashboard stopped")


def _cmd_dashboard_info() -> None:
    from .dashboard import info

    for k, v in info().items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
