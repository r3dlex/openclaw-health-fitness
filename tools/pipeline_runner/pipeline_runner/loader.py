"""YAML pipeline definition loader."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

import yaml

from pipeline_runner.errors import PipelineError
from pipeline_runner.pipeline import Pipeline


def load_pipeline(path: str | Path) -> Pipeline:
    """Load a pipeline from a YAML definition file.

    YAML format::

        name: my-pipeline
        description: What this pipeline does
        steps:
          - name: step_one
            function: module.path:function_name
            description: optional
            on_failure: stop|continue

    Args:
        path: Path to the YAML file.

    Returns:
        A configured ``Pipeline`` ready to run.

    Raises:
        PipelineError: If the file is invalid or functions can't be resolved.
    """
    path = Path(path)
    if not path.exists():
        raise PipelineError(f"Pipeline definition not found: {path}")

    with open(path) as f:
        try:
            defn = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise PipelineError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(defn, dict):
        raise PipelineError(f"Pipeline definition must be a mapping, got {type(defn).__name__}")

    name = defn.get("name")
    if not name:
        raise PipelineError("Pipeline definition missing 'name' field")

    steps_defn = defn.get("steps", [])
    if not steps_defn:
        raise PipelineError(f"Pipeline '{name}' has no steps defined")

    step_fns: list[Callable] = []
    for i, step_def in enumerate(steps_defn):
        func_ref = step_def.get("function")
        if not func_ref:
            raise PipelineError(f"Step {i} in pipeline '{name}' missing 'function' field")
        fn = _resolve_function(func_ref)
        step_fns.append(fn)

    return Pipeline(name=name, steps=step_fns)


def _resolve_function(ref: str) -> Callable:
    """Resolve a 'module.path:function_name' string to a callable.

    Args:
        ref: Dotted module path with colon-separated function name.

    Returns:
        The resolved callable.

    Raises:
        PipelineError: If the module or function can't be found.
    """
    if ":" not in ref:
        raise PipelineError(
            f"Invalid function reference '{ref}'. Expected 'module.path:function_name'."
        )

    module_path, func_name = ref.rsplit(":", 1)

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        raise PipelineError(f"Cannot import module '{module_path}': {exc}") from exc

    fn = getattr(module, func_name, None)
    if fn is None:
        raise PipelineError(f"Function '{func_name}' not found in module '{module_path}'")

    if not callable(fn):
        raise PipelineError(f"'{ref}' is not callable")

    return fn


def list_pipelines(directory: str | Path) -> list[dict[str, Any]]:
    """List all pipeline definitions in a directory.

    Returns:
        List of dicts with 'name', 'description', 'path', 'steps' count.
    """
    directory = Path(directory)
    pipelines = []

    for yaml_file in sorted(directory.glob("*.yaml")):
        try:
            with open(yaml_file) as f:
                defn = yaml.safe_load(f)
            if isinstance(defn, dict) and defn.get("name"):
                pipelines.append({
                    "name": defn["name"],
                    "description": defn.get("description", ""),
                    "path": str(yaml_file),
                    "steps": len(defn.get("steps", [])),
                })
        except Exception:
            continue

    return pipelines
