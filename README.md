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

## Testing

```bash
cd tools/pipeline_runner && poetry install --with dev && poetry run pytest
```

→ See [spec/TESTING.md](spec/TESTING.md) for full details.

## License

See [LICENSE](LICENSE).
