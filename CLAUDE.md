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
docker-dashboard/       ← Dashboard container (nginx + static HTML)
specs/                  ← Specification docs (→ see SPEC.md)
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
cd agent_helper && poetry install    # local dev without Docker
agent-helper daily                   # run directly
```

For architecture, data schemas, integrations: see `specs/ARCHITECTURE.md`.
