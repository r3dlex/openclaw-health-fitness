# Learnings

Timestamped entries capturing lessons learned during development and operation.

Format: `YYYY-MM-DD` — short description, context, and takeaway.

---

## 2026-03-23 — IAMQ registration requires workspace field

**Context:** First integration with the OpenClaw inter-agent message queue. Registration POST to `/register` returned 400 until the `workspace` field was added to the payload alongside `agent_id` and `capabilities`.

**Root cause:** The MQ server validates that every agent declares which workspace it belongs to. The field was undocumented at the time.

**Fix:** Added `"workspace": "openclaw"` to the registration payload in `agent_helper/agent_helper/mq.py`.

**Takeaway:** When integrating with shared infrastructure, test registration in isolation before wiring it into the main flow. Check the MQ server source for required fields — the API docs may lag behind.

> See: [COMMUNICATION.md](./COMMUNICATION.md) | [INTEGRATIONS.md](./INTEGRATIONS.md)
