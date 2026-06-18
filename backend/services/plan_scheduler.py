import json
from datetime import date, timedelta

def schedule_plan(json_structure: str, start_date: date) -> list[dict]:
    weeks = json.loads(json_structure)
    rows = []
    for week_data in weeks:
        week_num = week_data["week"]
        week_offset = (week_num - 1) * 7
        for day_data in week_data["days"]:
            day_num = day_data["day"]  # 1=Mon, 7=Sun
            day_offset = day_num - 1
            scheduled = start_date + timedelta(days=week_offset + day_offset)
            rows.append({
                "week": week_num,
                "day": day_num,
                "workout_type": day_data.get("workout_type"),
                "target_distance_km": day_data.get("target_distance_km"),
                "target_duration_mins": day_data.get("target_duration_mins"),
                "notes": day_data.get("notes"),
                "date_scheduled": scheduled,
            })
    return rows
