# Reporting

Reports are generated as Markdown files under `reports/`.

---

## Directory Structure

```
reports/
├── daily/YYYY/MM-DD.md
├── weekly/YYYY/Www.md
└── monthly/YYYY/MM.md
```

## Daily Report

Generated at 07:00 or on-demand via `python3 agent.py daily`.

Contains:
- Summary table: calories vs goal, protein vs goal, hydration vs goal
- Meal breakdown with individual calorie/protein counts
- Hydration log with net hydration calculations
- Steps count (from Health Connect)
- Sleep quality (when available)

## Weekly Report

Generated Sunday 20:00 or on-demand via `python3 agent.py weekly`.

Contains:
- 7-day totals and daily averages
- Per-day breakdown of calories, protein, hydration
- Goal adherence percentages
- Trend indicators

## Monthly Report

Generated 1st of month.

Contains:
- Macro trends over the month
- Weight trajectory
- Strategic adjustment recommendations
- Year-over-year comparison (when data available)

---

## Goals Reference

| Metric | Target | Range |
|--------|--------|-------|
| Calories | 2650 | 2500–2800 kcal |
| Protein | 180g | minimum |
| Hydration | 3000ml | minimum |
| Sleep | 8 hrs | target |
| Steps | 10,000 | target |
| Workouts | 4/week | target |
| Weight | 98 kg | from 114 kg |
