"""Report generation — daily, weekly, monthly markdown reports."""

from datetime import datetime, timedelta
from pathlib import Path

from .config import get_data_dir, get_reports_dir
from .data import filter_by_date, load_config, load_json


def calculate_daily(date_str: str, data_dir: Path | None = None) -> dict:
    """Calculate nutrition/hydration totals for a specific date."""
    if data_dir is None:
        data_dir = get_data_dir()

    nutrition = load_json(data_dir / "nutrition.json")
    hydration = load_json(data_dir / "hydration.json")

    meals = filter_by_date(nutrition, date_str)
    drinks = filter_by_date(hydration, date_str)

    return {
        "date": date_str,
        "meals": meals,
        "drinks": drinks,
        "calories": sum(m.get("estimated_calories", 0) for m in meals),
        "protein": sum(m.get("protein_grams", 0) for m in meals),
        "hydration_ml": sum(h.get("net_hydration_ml", 0) for h in drinks),
    }


def generate_daily_report(date_str: str, data_dir: Path | None = None) -> str:
    """Generate a daily health report as markdown."""
    if data_dir is None:
        data_dir = get_data_dir()

    data = calculate_daily(date_str, data_dir)
    goals = load_config(data_dir)

    cal_mid = (goals.get("min_daily_calories", 2500) + goals.get("max_daily_calories", 2800)) / 2
    protein_target = goals.get("min_daily_protein_g", 180)
    hydration_target = goals.get("min_daily_hydration_ml", 3000)

    cal_pct = f"{data['calories'] / cal_mid * 100:.0f}%" if cal_mid else "—"
    prot_pct = f"{data['protein'] / protein_target * 100:.0f}%" if protein_target else "—"
    hyd_pct = f"{data['hydration_ml'] / hydration_target * 100:.0f}%" if hydration_target else "—"

    cal_range = f"{goals.get('min_daily_calories', 2500)}-{goals.get('max_daily_calories', 2800)}"

    md = f"""# Daily Health Report - {date_str}

## Summary
| Metric | Value | Goal | % |
|--------|-------|------|---|
| Calories | {data['calories']} | {cal_range} | {cal_pct} |
| Protein | {data['protein']}g | {protein_target}g | {prot_pct} |
| Hydration | {data['hydration_ml']}ml | {hydration_target}ml | {hyd_pct} |

## Meals
"""
    for meal in data["meals"]:
        name = meal.get("food_name", "")
        kcal = meal.get("estimated_calories", 0)
        md += f"- **{meal.get('meal_type', 'meal')}**: {name} ({kcal} kcal)\n"

    md += "\n## Hydration\n"
    for drink in data["drinks"]:
        vol = drink.get("volume_ml", 0)
        net = drink.get("net_hydration_ml", 0)
        md += f"- {drink.get('beverage_type', '')}: {vol}ml -> {net}ml net\n"

    return md


def generate_weekly_report(week_start_date: str, data_dir: Path | None = None) -> str:
    """Generate a weekly health report from 7 daily reports."""
    if data_dir is None:
        data_dir = get_data_dir()

    start = datetime.fromisoformat(week_start_date)
    days = [(start + timedelta(days=i)).isoformat()[:10] for i in range(7)]
    week_data = [calculate_daily(d, data_dir) for d in days]
    goals = load_config(data_dir)

    cal_mid = (goals.get("min_daily_calories", 2500) + goals.get("max_daily_calories", 2800)) / 2
    protein_target = goals.get("min_daily_protein_g", 180)
    hydration_target = goals.get("min_daily_hydration_ml", 3000)

    total_cal = sum(d["calories"] for d in week_data)
    total_protein = sum(d["protein"] for d in week_data)
    total_hydration = sum(d["hydration_ml"] for d in week_data)
    avg_cal = total_cal / 7
    avg_protein = total_protein / 7
    avg_hydration = total_hydration / 7

    cal_range = f"{goals.get('min_daily_calories', 2500)}-{goals.get('max_daily_calories', 2800)}"

    md = f"""# Weekly Health Report - Week of {week_start_date}

## Weekly Summary
| Metric | Total | Daily Avg | Goal | % |
|--------|-------|-----------|------|---|
| Calories | {total_cal} | {avg_cal:.0f} | {cal_range} | {avg_cal / cal_mid * 100:.0f}% |
| Protein | {total_protein}g | {avg_protein:.0f}g | {protein_target}g | {avg_protein / protein_target * 100:.0f}% |
| Hydration | {total_hydration}ml | {avg_hydration:.0f}ml | {hydration_target}ml | {avg_hydration / hydration_target * 100:.0f}% |

## Daily Breakdown
"""
    for d in week_data:
        md += (
            f"- **{d['date']}**: "
            f"{d['calories']} kcal, "
            f"{d['protein']}g protein, "
            f"{d['hydration_ml']}ml hydration\n"
        )

    return md


def write_daily_report(date_str: str | None = None) -> Path:
    """Generate and write a daily report file. Returns the output path."""
    if date_str is None:
        date_str = datetime.now().isoformat()[:10]

    md = generate_daily_report(date_str)
    reports_dir = get_reports_dir()
    year = date_str[:4]
    month_day = date_str[5:]
    out_path = reports_dir / "daily" / year / f"{month_day}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(md)
    return out_path


def write_weekly_report(week_start: str | None = None) -> Path | None:
    """Generate and write a weekly report (Sunday only). Returns path or None."""
    now = datetime.now()
    if now.weekday() != 6:  # Sunday
        return None

    if week_start is None:
        week_start = (now - timedelta(days=6)).isoformat()[:10]

    md = generate_weekly_report(week_start)
    reports_dir = get_reports_dir()
    week_num = now.isocalendar()[1]
    year = str(now.year)
    out_path = reports_dir / "weekly" / year / f"W{week_num:02d}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(md)
    return out_path
