<p align="center">
  <img src="assets/logo.svg" alt="Health &amp; Fitness Agent logo" width="96" height="96">
</p>

# OpenClaw Health & Fitness Agent

Autonomous health tracking, reporting, and dashboarding — powered by [OpenClaw](https://docs.openclaw.ai).

## What It Does

Tracks nutrition, hydration, sleep, steps, weight, and activity from multiple sources. Generates daily/weekly reports. Serves a real-time dashboard.

## Quick Start

```bash
cp .env.example .env                           # configure paths & credentials
cd docker-dashboard && docker compose up -d    # start dashboard
python3 agent.py daily                         # generate today's report
```

Zero-install. Everything runs in Docker containers.

## Architecture

```
agent.py               → Entry point (delegates to Docker containers)
agent_helper/          → Python module with all business logic (Poetry + Docker)
tools/pipeline_runner/ → Generic step-based pipeline execution engine
docker-dashboard/      → Dashboard container (nginx + static HTML, port 8765)
spec/                  → Specification documents + ADRs
```

Data lives outside the repo at `$HEALTH_FITNESS_DATA_FOLDER` — see [.env.example](.env.example).

## Data Sources

| Source | Data | Method |
|--------|------|--------|
| Google Health Connect | Steps, sleep | Daily ZIP → SQLite import |
| Zepp Aura | Sleep quality, stages | Monthly summaries |
| Manual entry | Nutrition, hydration | JSON append |

## Documentation

| File | Audience | Content |
|------|----------|---------|
| [CLAUDE.md](CLAUDE.md) | Developers | Setup, development, architecture |
| [AGENTS.md](AGENTS.md) | OpenClaw agent | Operating manual, commands, autonomy |
| [spec/](spec/) | Both | Architecture, pipelines, testing, data schemas, ADRs |

## Inter-Agent Message Queue

This agent is registered as `health_fitness_agent` with the OpenClaw inter-agent MQ at `http://127.0.0.1:18790`. The MQ client lives in `agent_helper/agent_helper/mq.py`.

On every CLI invocation the agent registers, sends a heartbeat, and processes its inbox. After generating daily reports it broadcasts a summary to all peer agents (`mail_agent`, `librarian_agent`, `sysadmin_agent`, `workday_agent`, `journalist_agent`).

```bash
# Check inbox
curl -s http://127.0.0.1:18790/inbox/health_fitness_agent

# List online agents
curl -s http://127.0.0.1:18790/agents
```

## Testing

```bash
cd tools/pipeline_runner && poetry install --with dev && poetry run pytest
```

→ See [spec/TESTING.md](spec/TESTING.md) for full details.

## License

See [LICENSE](LICENSE).
