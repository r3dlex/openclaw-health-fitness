"""Pipeline and step error types."""


class PipelineError(Exception):
    """A pipeline-level failure (e.g. bad definition, load error)."""


class StepError(Exception):
    """A step raised an unrecoverable error."""


class StepSkipped(Exception):
    """A step was intentionally skipped (not a failure)."""
