# Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│  OpenClaw Platform                                          │
│  ┌───────────────┐    heartbeat/cron    ┌────────────────┐  │
│  │  Orchestrator  │ ──────────────────→ │  agent.py      │  │
│  └───────────────┘                      │  (entry point) │  │
│                                         └───────┬────────┘  │
└─────────────────────────────────────────────────┼───────────┘
                                                  │
                                                  ▼
                                    ┌─────────────────────────┐
                                    │  agent-helper (Docker)   │
                                    │  ┌───────┐ ┌──────────┐ │
                                    │  │reports │ │importers │ │
                                    │  └───┬───┘ └────┬─────┘ │
                                    │      │          │        │
                                    │  ┌───▼──────────▼─────┐ │
                                    │  │    data.py / config │ │
                                    │  └──────────┬─────────┘ │
                                    └─────────────┼───────────┘
                                                  │
                                    ┌─────────────▼───────────┐
                                    │  $HEALTH_FITNESS_DATA_   │
                                    │  FOLDER (external volume)│
                                    │  *.json files            │
                                    └─────────────┬───────────┘
                                                  │ mounted ro
                                    ┌─────────────▼───────────┐
                                    │  docker-dashboard        │
                                    │  nginx → index.html      │
                                    │  :8765                   │
                                    └─────────────────────────┘
```

## Components

### agent.py (entry point)

Thin wrapper at repo root. Loads `.env`, builds/runs the `agent-helper` Docker image. Falls back to direct Python import if Docker unavailable.

### agent_helper/ (Python module)

All business logic. Managed by Poetry, packaged as `agent-helper` CLI tool.

| Module | Responsibility |
|--------|---------------|
| `cli.py` | Command dispatcher |
| `config.py` | Environment loading, path resolution |
| `data.py` | JSON read/write, filtering |
| `reports.py` | Daily/weekly report generation |
| `importers.py` | Health Connect SQLite → JSON pipeline |
| `dashboard.py` | Docker container lifecycle |

### docker-dashboard/ (nginx container)

Static HTML dashboard served by nginx. Reads JSON data files via volume mount. No backend, no API — pure client-side rendering with CSS bar charts.

### specs/ (documentation)

Detached specification documents. Not code — reference material for both developers and the agent.

## Data Flow

```
Health Connect (Android phone)
    │
    ▼  ZIP export to Google Drive
Google Drive mount
    │
    ▼  agent-helper import
SQLite extraction → import_steps / import_sleep
    │
    ▼  JSON merge (append-only)
$HEALTH_FITNESS_DATA_FOLDER/*.json
    │
    ├──▶ Dashboard (nginx reads JSON, renders charts)
    └──▶ agent-helper daily/weekly (generates Markdown reports)
            │
            ▼
         reports/daily/YYYY/MM-DD.md
         reports/weekly/YYYY/Www.md
```

## Execution Model

| Trigger | Command | Schedule |
|---------|---------|----------|
| Cron | `python3 agent.py daily` | 07:00 daily |
| Cron | `python3 agent.py weekly` | Sunday 20:00 |
| Cron | `python3 agent.py import` | 08:45 daily |
| Heartbeat | Reads `HEARTBEAT.md` | Every ~30 min |
| Manual | `python3 agent.py report 2026-03-15` | On-demand |

## Key Decisions

- **External data folder**: Health data is personal — lives outside the repo, referenced by `$HEALTH_FITNESS_DATA_FOLDER`. Keeps git clean.
- **Docker-first**: All execution through containers. Zero local dependencies beyond Python 3 and Docker.
- **Append-only data**: Historical entries are never overwritten. New imports merge with existing data.
- **No external JS**: Dashboard uses pure CSS bar charts. No CDN dependencies, works fully offline.
- **Two audiences**: `CLAUDE.md` is for developers. `AGENTS.md` is for the OpenClaw agent. They don't duplicate each other.
