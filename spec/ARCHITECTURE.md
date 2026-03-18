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
                              ┌────────────────────┼────────────────────┐
                              │                    │                    │
                              ▼                    ▼                    ▼
                ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
                │  agent-helper    │  │  pipeline-runner  │  │  docker-dashboard │
                │  (Docker)        │  │  (Docker)         │  │  (nginx)          │
                │  reports,        │  │  step execution,  │  │  :8765            │
                │  importers       │  │  YAML pipelines   │  │                   │
                └────────┬─────────┘  └────────┬──────────┘  └────────┬──────────┘
                         │                     │                      │
                         └─────────┬───────────┘                      │
                                   │                                  │
                         ┌─────────▼──────────┐                       │
                         │  $HEALTH_FITNESS_   │                       │
                         │  DATA_FOLDER        │◀──────── mounted ro ──┘
                         │  (external volume)  │
                         │  *.json files       │
                         └─────────────────────┘
```

## Components

### agent.py (entry point)

Thin wrapper at repo root. Loads `.env`, builds/runs Docker images. Falls back to direct Python import if Docker unavailable. See [ADR-004](adr/004-docker-first-execution.md).

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

### tools/pipeline_runner/ (execution engine)

Generic step-based pipeline runner. No health-data knowledge — domain logic lives in bridge modules. See [ADR-001](adr/001-pipeline-runner-as-separate-module.md).

| Module | Responsibility |
|--------|---------------|
| `types.py` | `StepContext`, `StepResult`, `PipelineResult` dataclasses |
| `step.py` | `@step` decorator with retries, timing, error handling |
| `pipeline.py` | Sequential step orchestrator |
| `loader.py` | YAML pipeline definition parser |
| `runner.py` | CLI entry point |
| `bridges/` | Domain-specific step implementations |

→ Details: [spec/PIPELINES.md](PIPELINES.md)

### docker-dashboard/ (nginx container)

Static HTML dashboard served by nginx. Reads JSON data files via volume mount. No backend, no API — pure client-side rendering with CSS bar charts.

### spec/ (documentation)

Detached specification documents. Not code — reference material for both developers and the agent. Includes [Architecture Decision Records](adr/).

## Data Flow

```
Health Connect (Android phone)
    │
    ▼  ZIP export to Google Drive
Google Drive mount
    │
    ▼  pipeline-runner / agent-helper import
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
| Pipeline | `pipeline-runner run pipelines/health_connect_import.yaml` | On-demand |
| Heartbeat | Reads `HEARTBEAT.md` | Every ~30 min |
| Manual | `python3 agent.py report 2026-03-15` | On-demand |

## Key Decisions

Recorded as [Architecture Decision Records](adr/):

| ADR | Decision |
|-----|----------|
| [001](adr/001-pipeline-runner-as-separate-module.md) | Pipeline runner as a separate tools module |
| [002](adr/002-steps-as-plain-functions.md) | Steps as plain functions with decorator protocol |
| [003](adr/003-declarative-yaml-pipelines.md) | Declarative YAML pipeline definitions |
| [004](adr/004-docker-first-execution.md) | Docker-first execution with host fallback |
| [005](adr/005-structured-step-observability.md) | Structured logging and step-level observability |

## Design Principles

- **External data folder**: Health data is personal — lives outside the repo, referenced by `$HEALTH_FITNESS_DATA_FOLDER`. Keeps git clean.
- **Docker-first**: All execution through containers. Zero local dependencies beyond Python 3 and Docker.
- **Append-only data**: Historical entries are never overwritten. New imports merge with existing data.
- **No external JS**: Dashboard uses pure CSS bar charts. No CDN dependencies, works fully offline.
- **Two audiences**: `CLAUDE.md` is for developers. `AGENTS.md` is for the OpenClaw agent. They don't duplicate each other.
- **Testable steps**: Every pipeline step is a plain function testable in isolation. See [spec/TESTING.md](TESTING.md).
