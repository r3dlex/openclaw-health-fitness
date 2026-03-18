"""CLI entry point for the pipeline runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pipeline_runner.loader import list_pipelines, load_pipeline
from pipeline_runner.types import StepContext


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point. Returns exit code."""
    parser = argparse.ArgumentParser(
        prog="pipeline-runner",
        description="Execute step-based pipelines from YAML definitions.",
    )
    sub = parser.add_subparsers(dest="command")

    # run
    run_p = sub.add_parser("run", help="Run a pipeline")
    run_p.add_argument("pipeline", help="Path to pipeline YAML file")
    run_p.add_argument("--dry-run", action="store_true", help="Validate without executing side effects")
    run_p.add_argument("--config", type=str, default=None, help="JSON string of config overrides")

    # list
    list_p = sub.add_parser("list", help="List available pipelines")
    list_p.add_argument("--dir", default="pipelines", help="Directory containing pipeline YAML files")

    # validate
    val_p = sub.add_parser("validate", help="Validate a pipeline definition")
    val_p.add_argument("pipeline", help="Path to pipeline YAML file")

    args = parser.parse_args(argv)

    if args.command == "run":
        return _cmd_run(args)
    elif args.command == "list":
        return _cmd_list(args)
    elif args.command == "validate":
        return _cmd_validate(args)
    else:
        parser.print_help()
        return 0


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute a pipeline."""
    pipeline = load_pipeline(args.pipeline)

    config: dict = {}
    if args.config:
        try:
            config = json.loads(args.config)
        except json.JSONDecodeError as exc:
            print(f"Error: Invalid --config JSON: {exc}", file=sys.stderr)
            return 1

    ctx = StepContext(config=config, dry_run=args.dry_run)
    result = pipeline.run(ctx)

    print(result.to_json(indent=2))

    return 0 if result.ok else 1


def _cmd_list(args: argparse.Namespace) -> int:
    """List available pipelines."""
    pipelines = list_pipelines(args.dir)
    if not pipelines:
        print(f"No pipelines found in {args.dir}/")
        return 0

    for p in pipelines:
        print(f"  {p['name']:<30} {p['steps']} steps  {p['description']}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Validate a pipeline definition without running it."""
    try:
        pipeline = load_pipeline(args.pipeline)
        print(f"Valid: {pipeline.name} ({len(pipeline.steps)} steps)")
        return 0
    except Exception as exc:
        print(f"Invalid: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
