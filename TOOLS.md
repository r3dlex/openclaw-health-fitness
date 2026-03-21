# TOOLS.md - Environment Notes

Environment-specific configuration for this agent's setup.

## Inter-Agent Message Queue

- **HTTP API**: http://127.0.0.1:18790
- **WebSocket**: ws://127.0.0.1:18791/ws
- **Agent ID**: `health_fitness_agent`
- **MQ client**: `agent_helper/agent_helper/mq.py`
- **File fallback**: `~/Ws/Openclaw/openclaw-inter-agent-message-queue/queue/health_fitness_agent/`
- **Protocol docs**: `~/Ws/Openclaw/openclaw-inter-agent-message-queue/spec/PROTOCOL.md`

## Dashboard

- **URL**: http://localhost:8765
- **Container**: `docker-dashboard/docker-compose.yml`
- **Data mount**: `$HEALTH_FITNESS_DATA_FOLDER` → read-only in container

## Data Storage

- **Location**: `$HEALTH_FITNESS_DATA_FOLDER` (set in `.env`)
- **Files**: `config.json`, `steps.json`, `sleep.json`, `nutrition.json`, `body_metrics.json`
- **Schema**: `spec/DATA_SCHEMA.md`

## Cron

- **Daily health sync**: `0 9 * * *` — runs `python3 agent.py daily`
- **Log**: `logs/daily.log`

## Docker

- **Agent helper image**: `agent-helper:latest` (auto-builds on first run)
- **Dashboard**: `docker compose -f docker-dashboard/docker-compose.yml up -d`

---

Add whatever helps you do your job. This is your cheat sheet.
