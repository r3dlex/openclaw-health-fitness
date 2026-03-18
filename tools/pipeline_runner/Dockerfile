FROM python:3.11-slim
WORKDIR /app

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml ./
RUN poetry install --only main --no-interaction --no-ansi 2>/dev/null || true

COPY pipeline_runner/ pipeline_runner/
COPY pipelines/ pipelines/
RUN poetry install --only main --no-interaction --no-ansi

ENTRYPOINT ["pipeline-runner"]
