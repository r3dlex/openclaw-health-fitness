# HEARTBEAT.md

Recurring tasks the agent performs on each session and periodically.

## Inter-Agent Message Queue

### Heartbeat (every session)

```bash
curl -s -X POST http://127.0.0.1:18790/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"agent_id": "health_fitness_agent"}'
```

### Check inbox (every session)

```bash
curl -s http://127.0.0.1:18790/inbox/health_fitness_agent?status=unread
```

Process each unread message:
1. Read and understand the message content.
2. If `type: "request"` — act on it and reply via `POST /send` with `replyTo` set to the original message `id`.
3. If `type: "info"` — acknowledge if relevant.
4. Mark handled messages as acted:

```bash
curl -s -X PATCH http://127.0.0.1:18790/messages/:id \
  -H 'Content-Type: application/json' \
  -d '{"status": "acted"}'
```

### Reply pattern

When replying to another agent's message, always use the MQ — not Telegram:

```bash
curl -s -X POST http://127.0.0.1:18790/send \
  -H 'Content-Type: application/json' \
  -d '{
    "from": "health_fitness_agent",
    "to": "<requesting_agent_id>",
    "type": "response",
    "priority": "NORMAL",
    "subject": "Re: <original subject>",
    "body": "<response content>",
    "replyTo": "<original-message-uuid>"
  }'
```

## Daily Health Sync

- **Schedule:** 9AM daily (cron)
- **Command:** `python3 agent.py daily`
- **Post-run:** Broadcast summary to all agents via MQ.

## Dashboard Check

- Verify dashboard is running at http://localhost:8765
- Check data freshness in `$HEALTH_FITNESS_DATA_FOLDER`
