FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

# Copy project files
COPY pyproject.toml README.md ./
COPY agent_helper/ agent_helper/

# Install package
RUN poetry install --only main --no-interaction

ENTRYPOINT ["agent-helper"]
