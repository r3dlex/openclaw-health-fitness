# BOOT.md

Startup sequence for the health_fitness_agent.

## 1. Register with the Inter-Agent Message Queue

```bash
curl -s -X POST http://127.0.0.1:18790/register \
  -H 'Content-Type: application/json' \
  -d '{
    "agent_id": "health_fitness_agent",
    "name": "FitBot",
    "emoji": "💪",
    "description": "Health data imports, daily reports, and dashboard management",
    "capabilities": [
      "health_data_import",
      "daily_report",
      "weekly_report",
      "dashboard_management",
      "steps_tracking",
      "sleep_tracking",
      "hydration_tracking",
      "weight_tracking",
      "pipeline_execution"
    ]
  }'
```

## 2. Send initial heartbeat

```bash
curl -s -X POST http://127.0.0.1:18790/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"agent_id": "health_fitness_agent"}'
```

## 3. Check inbox for pending messages

```bash
curl -s http://127.0.0.1:18790/inbox/health_fitness_agent?status=unread
```

Process any unread messages before starting regular work.

## 4. Verify environment

- `HEALTH_FITNESS_DATA_FOLDER` is set and accessible
- Dashboard container is running (`docker compose -f docker-dashboard/docker-compose.yml ps`)
- Data files exist: `config.json`, `steps.json`, `sleep.json`, `nutrition.json`, `body_metrics.json`

## 5. Announce online (first session only)

```bash
curl -s -X POST http://127.0.0.1:18790/send \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "health_fitness_agent",
    "to": "broadcast",
    "type": "info",
    "priority": "NORMAL",
    "subject": "health_fitness_agent online",
    "body": "Health fitness agent is online. Manages health data imports (Health Connect, Zepp), daily/weekly reports, and dashboard at localhost:8765. Send requests for health data operations."
  }'
```
