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
agent.py           → Entry point (delegates to agent-helper Docker container)
agent_helper/      → Python module with all business logic (Poetry + Docker)
docker-dashboard/  → Dashboard container (nginx + static HTML, port 8765)
specs/             → Specification documents
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
| [specs/](specs/) | Both | Data schemas, integrations, reporting |

## License

See [LICENSE](LICENSE).
