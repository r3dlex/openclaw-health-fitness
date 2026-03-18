# CLAUDE.md

**OpenClaw Health & Fitness Agent** — autonomous health tracking, reporting, and dashboarding.

## Quick Start

```bash
cp .env.example .env                           # configure paths & credentials
cd docker-dashboard && docker compose up -d    # dashboard → http://localhost:8765
python3 agent.py daily                         # auto-builds Docker image on first run
```

Zero-install. Everything runs in Docker.

## Repo Layout

```
agent.py               ← Entry point (thin Docker wrapper)
agent_helper/           ← Python module — all business logic
  pyproject.toml        ← Poetry config
  Dockerfile            ← Zero-install container
  agent_helper/         ← Package: cli, config, data, reports, importers, dashboard
tools/
  pipeline_runner/      ← Generic pipeline execution engine
    pyproject.toml      ← Poetry config
    Dockerfile          ← Zero-install container
    pipeline_runner/    ← Package: types, step, pipeline, loader, runner, bridges
    pipelines/          ← YAML pipeline definitions
    tests/              ← Unit + integration tests
docker-dashboard/       ← Dashboard container (nginx + static HTML)
spec/                   ← Specification docs (→ see SPEC.md)
  adr/                  ← Architecture Decision Records
```

### OpenClaw agent files (read by FitBot, not by you)

`AGENTS.md` · `SOUL.md` · `IDENTITY.md` · `USER.md` · `TOOLS.md` · `HEARTBEAT.md`

### What's gitignored

`data/` · `reports/` · `logs/` · `.env` · `.openclaw/`

## Environment

All config via `.env` — see `.env.example`. Key variable:

- `HEALTH_FITNESS_DATA_FOLDER` — where JSON data lives (external to repo)

## Development

```bash
# Agent helper (local dev without Docker)
cd agent_helper && poetry install && agent-helper daily

# Pipeline runner
cd tools/pipeline_runner && poetry install --with dev
pipeline-runner run pipelines/health_connect_import.yaml

# Run tests
cd tools/pipeline_runner && poetry run pytest -v
```

## Further Reading

- Architecture, data flow: [spec/ARCHITECTURE.md](spec/ARCHITECTURE.md)
- Pipelines, steps, YAML definitions: [spec/PIPELINES.md](spec/PIPELINES.md)
- Testing strategy, coverage: [spec/TESTING.md](spec/TESTING.md)
- Data schemas: [spec/DATA_SCHEMA.md](spec/DATA_SCHEMA.md)
- Architecture decisions: [spec/adr/](spec/adr/)
