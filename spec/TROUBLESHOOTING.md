# Troubleshooting

Common issues and how to fix them.

---

## Docker / Container Issues

### Container won't start

```
Error: Cannot connect to the Docker daemon
```

Docker Desktop must be running. Verify with `docker info`.

### Image build fails

```bash
# Force a clean rebuild
docker build --no-cache -t agent-helper -f agent_helper/Dockerfile agent_helper
```

Check that `pyproject.toml` dependencies resolve. Poetry lock issues inside the container usually mean a stale `poetry.lock`.

### Volume mount errors

```
Error: Mounts denied: path not shared from the host
```

Ensure `$HEALTH_FITNESS_DATA_FOLDER` is an absolute path and is listed in Docker Desktop > Settings > Resources > File Sharing. The data folder must exist before the container starts.

### Dashboard container shows no data

The dashboard mounts the data folder as read-only. Verify:

```bash
docker exec -it openclaw-dashboard ls /data
```

If empty, check that `HEALTH_FITNESS_DATA_FOLDER` is set correctly in `.env` and that `docker-compose.yml` references it.

---

## Data Import Failures

### Missing export file

```
FileNotFoundError: No ZIP file found in import path
```

Health Connect exports land in Google Drive. Confirm the ZIP is present:

```bash
ls "$HEALTH_FITNESS_DATA_FOLDER"/imports/*.zip
```

If missing, trigger a manual export from the Health Connect app.

### Wrong file format

The importer expects Health Connect SQLite-inside-ZIP. Other formats (CSV, plain JSON) are not supported by the default import pipeline. See [INTEGRATIONS.md](./INTEGRATIONS.md) for supported sources.

### Parser errors on import

```
sqlite3.DatabaseError: file is not a database
```

The ZIP may be corrupt or partially downloaded. Re-export from Health Connect and retry. The importer never overwrites existing data, so re-running is safe.

### Duplicate data after re-import

The append-only merge deduplicates by timestamp + metric type. If duplicates appear, check that the source data has consistent timestamps. See [DATA_SCHEMA.md](./DATA_SCHEMA.md) for dedup rules.

---

## Report Generation

### Template errors

```
KeyError: 'calories'
```

A required data key is missing from the day's JSON. This usually means the import didn't run or produced no entries for that date. Run `python3 agent.py import` first, then retry the report.

### Empty report generated

The report generator skips days with zero data entries. Check:

1. Data exists for the target date in `$HEALTH_FITNESS_DATA_FOLDER`
2. The date format matches `YYYY-MM-DD`
3. JSON files are valid (no trailing commas, no truncation)

### Report not appearing in dashboard

Reports live under `reports/daily/YYYY/MM-DD.md`. The dashboard reads from the data folder, not the reports folder. If you need report content on the dashboard, verify the JSON data files are up to date.

---

## Dashboard

### Rendering issues

The dashboard is pure static HTML with CSS bar charts — no JavaScript frameworks. If bars don't render:

- Hard-refresh the browser (`Cmd+Shift+R`)
- Check that the JSON data files are valid
- Inspect the browser console for JSON parse errors

### Stale data

The dashboard reads JSON files on page load. If data looks outdated:

1. Confirm the import ran: `python3 agent.py import`
2. Confirm the data folder has today's entries
3. Restart the dashboard container: `cd docker-dashboard && docker compose restart`

---

## IAMQ Integration

### Registration fails

```
ConnectionError: http://127.0.0.1:18790/register
```

The inter-agent MQ must be running. Start it:

```bash
cd ~/Ws/Openclaw/openclaw-inter-agent-message-queue && python3 server.py
```

### MQ unreachable after registration

The agent registers on every CLI invocation. If the MQ goes down mid-session, the agent logs a warning and continues — MQ is non-blocking. On next invocation it will re-register.

### Messages not delivered

Check the inbox manually:

```bash
curl -s http://127.0.0.1:18790/inbox/health_fitness_agent
```

If the HTTP endpoint is down, check the file-based fallback queue:

```
~/Ws/Openclaw/openclaw-inter-agent-message-queue/queue/health_fitness_agent/
```

See [COMMUNICATION.md](./COMMUNICATION.md) for the dual-mode pattern.

---

> Related: [ARCHITECTURE.md](./ARCHITECTURE.md) | [INTEGRATIONS.md](./INTEGRATIONS.md) | [COMMUNICATION.md](./COMMUNICATION.md)
