"""Pure transformations of verified upstream response fields."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Reading:
    value: float | str | None
    unit: str | None
    daily: bool = True
    name: str | None = None
    date: str | None = None
    numeric: bool = True


def number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if isfinite(result) else None
    except (TypeError, ValueError):
        return None


BODY_UNITS = {
    "weight": "kg",
    "neck": "cm",
    "waist": "cm",
    "hips": "cm",
    "height": "cm",
    "body_fat_percentage": "%",
    "muscle_mass_kg": "kg",
    "bone_mass_kg": "kg",
    "body_water_percentage": "%",
    "steps": None,
    "bmr": "kcal",
    "resting_heart_rate": "bpm",
}
UNIT_ALIASES = {
    "minutes": "min",
    "seconds": "s",
    "hours": "h",
    "ml": "mL",
    "count": None,
    "N/A": None,
}


def parse_snapshot(raw: dict) -> dict[str, Reading]:
    out = {}
    day = raw["day"]

    def add(key, value, unit, daily=True, name=None, date=None, numeric=True):
        out[key] = Reading(number(value) if numeric else value, unit, daily, name, date, numeric)

    body = raw.get("body") or {}
    for field, unit in BODY_UNITS.items():
        if field in body:
            add(field, body[field], unit, field in ("steps", "bmr"))
    summary = raw.get("summary") or {}
    balance = summary.get("calorieBalance") or {}
    if isinstance(balance, dict):
        for source, key in (
            ("eaten", "calories"),
            ("goal", "calories_goal"),
            ("remaining", "calories_remaining"),
            ("burned", "calories_burned"),
        ):
            if source in balance:
                add(key, balance[source], "kcal")
    goals = summary.get("goals") or {}
    adjusted = summary.get("adjustedGoals") or {}
    if not isinstance(goals, dict):
        goals = {}
    if not isinstance(adjusted, dict):
        adjusted = {}
    entries = summary.get("foodEntries")
    supplements = summary.get("supplementTotals") or {}
    for nutrient in ("protein", "carbs", "fat", "dietary_fiber", "sugars", "sodium"):
        unit = "mg" if nutrient == "sodium" else "g"
        if nutrient in goals or nutrient in adjusted:
            add(nutrient + "_goal", adjusted.get(nutrient, goals.get(nutrient)), unit)
        if isinstance(entries, list):
            total = 0.0
            valid = True
            for entry in entries:
                if not isinstance(entry, dict):
                    valid = False
                    break
                value, quantity, size = (
                    number(entry.get(k)) for k in (nutrient, "quantity", "serving_size")
                )
                if value is None or quantity is None or size is None or size <= 0:
                    valid = False
                    break
                total += value * quantity / size
            supplement = (
                number(supplements.get(nutrient, 0)) if isinstance(supplements, dict) else None
            )
            add(nutrient, total + supplement if valid and supplement is not None else None, unit)
    if "waterIntake" in summary:
        add("water", summary["waterIntake"], "mL")
    sessions = summary.get("exerciseSessions")
    if isinstance(sessions, list):
        durations = []
        for session in sessions:
            if not isinstance(session, dict):
                durations.append(None)
                continue
            if (session.get("exercise_snapshot") or {}).get("name") == "Active Calories":
                continue
            durations.append(
                number(
                    session.get(
                        "total_duration_minutes"
                        if session.get("type") == "preset"
                        else "duration_minutes"
                    )
                )
            )
        add("training_count", len(durations), None)
        add(
            "training_duration",
            sum(durations) if all(v is not None for v in durations) else None,
            "min",
        )
    categories = {c["id"]: c for c in raw.get("categories") or [] if isinstance(c.get("id"), str)}
    for cid, category in categories.items():
        daily = category.get("frequency") != "All"
        rows = [
            r
            for r in raw.get("custom") or []
            if r.get("category_id") == cid
            and isinstance(r.get("entry_date"), str)
            and r["entry_date"][:10] <= day
            and (not daily or r["entry_date"][:10] == day)
        ]
        latest = max(
            rows,
            key=lambda r: (
                r.get("entry_date", ""),
                r.get("entry_timestamp") or "",
                r.get("entry_hour") or 0,
            ),
            default={},
        )
        numeric = category.get("data_type") != "text"
        value = latest.get("value")
        if not numeric:
            value = value[:255] if isinstance(value, str) else None
        unit = category.get("measurement_type") if numeric else None
        if not isinstance(unit, str) or len(unit) > 32:
            unit = None
        add(
            f"custom_{cid}",
            value,
            UNIT_ALIASES.get(unit, unit),
            daily,
            str(category.get("display_name") or category.get("name") or cid)[:255],
            latest.get("entry_date"),
            numeric,
        )
    sleep = raw.get("sleep") or []
    # Longest sleep record avoids summing overlapping records from multiple providers.
    sleep = [r for r in sleep if str(r.get("entry_date", ""))[:10] == day]
    latest = max(sleep, key=lambda r: number(r.get("duration_in_seconds")) or 0, default={})
    for field, unit in (
        ("duration_in_seconds", "s"),
        ("time_asleep_in_seconds", "s"),
        ("sleep_score", None),
        ("deep_sleep_seconds", "s"),
        ("rem_sleep_seconds", "s"),
        ("light_sleep_seconds", "s"),
        ("average_spo2_value", "%"),
        ("avg_overnight_hrv", "ms"),
    ):
        if field in latest:
            add("sleep_" + field, latest[field], unit)
    return out
