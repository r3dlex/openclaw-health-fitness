# Safety

Boundaries and constraints for the health & fitness agent.

---

## Health Data is PII

All health data (weight, heart rate, sleep, blood pressure, nutrition logs) is personally identifiable information. Rules:

- **Never share raw data via IAMQ broadcasts.** Outbound messages contain summaries and percentages only.
- **Never include raw measurements in message bodies.** A broadcast may say "calorie goal 95% met" but never "2520 kcal consumed."
- **Data folder stays local.** `$HEALTH_FITNESS_DATA_FOLDER` is never exposed to other agents or external services.
- **Logs are scrubbed.** Log lines reference dates and statuses, not values.

## Reports Are Summaries Only

Messages sent to other agents via the MQ contain:

| Allowed | Not Allowed |
|---------|-------------|
| Goal adherence % | Actual calorie counts |
| Trend direction (up/down/stable) | Specific weight values |
| Alert flags (threshold breached) | Blood pressure readings |
| Sleep quality rating | Raw sleep stage data |

Full reports with raw data exist only as local Markdown files under `reports/`. See [REPORTING.md](./REPORTING.md).

## No Medical Advice

The agent analyzes data and tracks trends. It does **not**:

- Diagnose conditions
- Recommend medications or supplements
- Interpret lab results
- Suggest treatment plans
- Override user-set thresholds without consent

Alerts are factual: "Blood pressure reading above configured threshold" — not "You may have hypertension."

## Rate Limits

| Resource | Limit | Rationale |
|----------|-------|-----------|
| MQ messages per invocation | 5 | Prevent broadcast storms |
| Import retries | 3 | Avoid hammering a failing source |
| Dashboard restarts per hour | 2 | Prevent restart loops |

External API calls (Google Drive, future integrations) must respect upstream rate limits. The agent backs off exponentially on 429 responses.

## Data Retention

- **Raw JSON data:** Retained indefinitely in `$HEALTH_FITNESS_DATA_FOLDER`. Append-only, never deleted.
- **Reports:** Retained indefinitely under `reports/`. Can be manually pruned.
- **MQ messages:** Processed and marked as read. No local copy retained after processing.
- **Logs:** Rotated by the host system. No sensitive values in log output.

## Backup Before Correction

Per [AGENT_SPEC.md](./AGENT_SPEC.md), the agent never overwrites historical data. When a correction is needed:

1. Preserve the original value
2. Append the corrected entry with a `corrected: true` flag
3. Log the correction reason

---

> Related: [AGENT_SPEC.md](./AGENT_SPEC.md) | [COMMUNICATION.md](./COMMUNICATION.md) | [DATA_SCHEMA.md](./DATA_SCHEMA.md)
