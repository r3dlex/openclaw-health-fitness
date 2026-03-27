FROM python:3.11-slim

WORKDIR /app

# Install system deps: unzip (extract HC backups), curl (downloads), docker CLI
RUN apt-get update && apt-get install -y --no-install-recommends unzip curl && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://download.docker.com/linux/static/stable/aarch64/docker-26.0.0.tgz -o /tmp/docker.tgz \
    && tar -xzf /tmp/docker.tgz -C /tmp \
    && mv /tmp/docker/docker /usr/local/bin/ \
    && rm -rf /tmp/docker*

# Install Poetry
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

# Copy project files
COPY pyproject.toml README.md ./
COPY agent_helper/ agent_helper/

# Install package
RUN poetry install --only main --no-interaction

ENTRYPOINT ["agent-helper"]
