# Integrations

Health data sources and their connection status.

---

## Active

### Google Health Connect
- **Data:** Steps, heart rate, sleep, weight, blood pressure, exercise
- **Method:** Daily ZIP export via Google Drive → SQLite → JSON
- **Schedule:** 8:45 AM daily (data is always from previous day)
- **Command:** `python3 agent.py import`

### Zepp Aura
- **Data:** Sleep duration, quality (deep/REM %), bedtime/wake patterns
- **Method:** Monthly summaries imported from Zepp app
- **History:** Oct 2020 — present

---

## Planned

### Renpho Health
- **Data:** Weight, body composition, BMI, muscle mass, body fat %
- **Method:** Bluetooth sync via Renpho app
- **Status:** Pending setup

### iHealth
- **Data:** Blood pressure, heart rate, blood glucose, SpO2
- **Method:** Bluetooth + iHealth API
- **Status:** Pending setup

### Solos Brille
- **Data:** Activity tracking, UV exposure, step count
- **Method:** Smart glasses via Solos app
- **Status:** Pending setup

---

## Deduplication Rules

When multiple sources report the same metric:

| Metric | Preferred | Fallback |
|--------|-----------|----------|
| Steps | Zepp | Health Connect |
| Sleep | Zepp | Health Connect |
| Weight | Renpho | Manual |

---

## Adding a New Integration

1. Add config entry in `config.json` under `integrations`
2. Add importer function in `agent_helper/agent_helper/importers.py`
3. Wire it into `cli.py`
4. Document data format in [DATA_SCHEMA.md](./DATA_SCHEMA.md)
5. Update this file
