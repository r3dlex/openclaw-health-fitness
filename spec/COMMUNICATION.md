# Communication

IAMQ (Inter-Agent Message Queue) messaging patterns for the health & fitness agent.

---

## Agent Identity

| Field | Value |
|-------|-------|
| Agent ID | `health_fitness_agent` |
| MQ Endpoint | `http://127.0.0.1:18790` |
| Capabilities | `health_tracking`, `daily_reports`, `weekly_reports`, `data_import` |
| Workspace | `openclaw` |

## Registration

On every CLI invocation, the agent:

1. POSTs `/register` with `agent_id`, `capabilities`, and `workspace`
2. Sends a heartbeat to `/heartbeat`
3. Processes inbox (see below)

Registration is idempotent. Re-registering updates the last-seen timestamp.

## Outbound Messages

### Daily report broadcast

After each daily report generation, the agent broadcasts a summary to all registered agents:

```json
{
  "from": "health_fitness_agent",
  "to": "*",
  "type": "broadcast",
  "priority": "NORMAL",
  "subject": "Daily Health Report — 2026-03-23",
  "body": "<summary only, no raw data>"
}
```

The body contains goal adherence percentages and alerts — never raw measurements. See [SAFETY.md](./SAFETY.md).

## Inbox Processing

On every invocation, the agent reads all pending messages:

1. Fetches `GET /inbox/health_fitness_agent`
2. Logs each message (sender, type, subject)
3. Marks each message as read via `POST /inbox/health_fitness_agent/read`

All message types are logged. No automated responses — the agent is a producer, not a conversational peer.

## Peer Agents

| Agent | Relationship |
|-------|-------------|
| `main` | Orchestrator. Receives daily/weekly report broadcasts. Routes user requests to this agent. |
| `mail_agent` | Peer. No direct interaction currently. |
| `librarian_agent` | Peer. No direct interaction currently. |
| `sysadmin_agent` | Peer. No direct interaction currently. |
| `workday_agent` | Peer. No direct interaction currently. |
| `journalist_agent` | Peer. No direct interaction currently. |

## Dual-Mode Delivery

The MQ client uses two delivery modes:

1. **HTTP (primary):** REST calls to `http://127.0.0.1:18790`. Used when the MQ server is reachable.
2. **File-based (fallback):** Writes JSON message files to `~/Ws/Openclaw/openclaw-inter-agent-message-queue/queue/health_fitness_agent/`. Used when HTTP fails.

The client tries HTTP first. On connection error, it falls back to file-based delivery and logs a warning. No messages are lost — the MQ server picks up file-based messages on its next sweep.

```python
# Simplified flow in mq.py
try:
    post(f"{MQ_URL}/send", payload)
except ConnectionError:
    write_to_file_queue(payload)
    log.warning("MQ unreachable, used file fallback")
```

---

> Related: [SAFETY.md](./SAFETY.md) | [ARCHITECTURE.md](./ARCHITECTURE.md) | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
