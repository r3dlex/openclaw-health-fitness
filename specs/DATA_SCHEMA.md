# Data Schema

All data files are JSON, stored in `$HEALTH_FITNESS_DATA_FOLDER`.

---

## config.json

Agent configuration: integrations, user constraints, deduplication rules.

```jsonc
{
  "user_constraints": {
    "height_cm": 192,
    "current_weight_kg": 114,
    "weight_goal_kg": 98,
    "min_daily_calories": 2500,
    "max_daily_calories": 2800,
    "min_daily_protein_g": 180,
    "min_daily_hydration_ml": 3000,
    "sleep_target_hrs": 8,
    "steps_target": 10000,
    "workout_days_per_week": 4
  }
}
```

---

## nutrition.json

Array of meal entries.

```jsonc
[
  {
    "timestamp": "2026-02-21T08:00:00",
    "meal_type": "breakfast",        // breakfast | lunch | dinner | snack
    "food_name": "High-protein yogurt",
    "estimated_calories": 180,
    "protein_grams": 20,
    "source": "manual"
  }
]
```

---

## hydration.json

Array of fluid intake entries.

```jsonc
[
  {
    "timestamp": "2026-02-21T07:30:00",
    "volume_ml": 500,
    "beverage_type": "water",
    "net_hydration_factor": 1.0,
    "net_hydration_ml": 500,
    "source": "manual"
  }
]
```

---

## steps.json

Aggregated step counts by date.

```jsonc
{
  "total_steps": 422101,
  "by_date": {
    "2026-03-15": 8432
  },
  "last_updated": "2026-03-17T10:05:00",
  "source": "health_connect"
}
```

---

## sleep.json

Array of monthly sleep summaries (historical) + daily entries from Health Connect.

```jsonc
// Monthly summary (Zepp Aura)
{
  "date": "2026-02",
  "duration_hours": 6.2,
  "deep_sleep_pct": 0.24,
  "rem_sleep_pct": 0.16,
  "bedtime": "00:15",
  "wake_time": "06:30"
}

// Daily entry (Health Connect)
{
  "date": "2026-03-14",
  "duration_hours": 7.5,
  "duration_minutes": 450,
  "source": "health_connect"
}
```

---

## body_metrics.json

Weight tracking by date.

```jsonc
{
  "by_date": {
    "2026-03-09": 116.5
  }
}
```

---

## activity.json

Array of workout/activity entries.

```jsonc
[
  {
    "timestamp": "2026-02-21T18:00:00",
    "type": "strength_training",
    "duration_min": 60,
    "calories_burned": 450,
    "source": "zepp"
  }
]
```

---

## vitals.json

Blood pressure, heart rate, glucose, SpO2 — currently empty, awaiting iHealth integration.

## integration_logs.json

Array of sync status entries for audit trail.
