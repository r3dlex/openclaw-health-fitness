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

## Inter-Agent Message Queue

This agent (`health_fitness_agent`) is registered with the OpenClaw inter-agent MQ at `http://127.0.0.1:18790`. The MQ client lives in `agent_helper/agent_helper/mq.py`.

At every CLI invocation, the agent registers, sends a heartbeat, and processes its inbox. After daily reports, it broadcasts a summary to all agents.

Other agents in the environment: `mail_agent`, `librarian_agent`, `sysadmin_agent`, `workday_agent`, `journalist_agent`.

To check inbox or send messages manually:

```bash
# Check inbox
curl -s http://127.0.0.1:18790/inbox/health_fitness_agent

# Send a message
curl -s -X POST http://127.0.0.1:18790/send -H 'Content-Type: application/json' \
  -d '{"from":"health_fitness_agent","to":"mail_agent","type":"request","priority":"NORMAL","subject":"Test","body":"Hello"}'

# List online agents
curl -s http://127.0.0.1:18790/agents
```

File-based fallback queue: `~/Ws/Openclaw/openclaw-inter-agent-message-queue/queue/health_fitness_agent/`

## Further Reading

- Architecture, data flow: [spec/ARCHITECTURE.md](spec/ARCHITECTURE.md)
- Pipelines, steps, YAML definitions: [spec/PIPELINES.md](spec/PIPELINES.md)
- Testing strategy, coverage: [spec/TESTING.md](spec/TESTING.md)
- Data schemas: [spec/DATA_SCHEMA.md](spec/DATA_SCHEMA.md)
- Architecture decisions: [spec/adr/](spec/adr/)
