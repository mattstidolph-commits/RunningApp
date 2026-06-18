import fitparse
from datetime import timezone

SPORT_MAP = {
    "running": "run",
    "cycling": "other",
    "training": "crossfit",
    "walking": "walk",
}

def parse_fit_file(path: str) -> dict:
    fit = fitparse.FitFile(path)
    session = next(fit.get_messages("session"), None)
    if session is None:
        raise ValueError(f"No session message found in {path}")

    def val(name):
        return session.get_value(name)

    start_time = val("start_time")
    if hasattr(start_time, "replace"):
        date_str = start_time.strftime("%Y-%m-%d")
        garmin_id = start_time.strftime("%Y%m%d%H%M%S")
    else:
        date_str = str(start_time)[:10]
        garmin_id = str(start_time).replace("-", "").replace(":", "").replace(" ", "")

    sport_raw = val("sport") or "other"
    activity_type = SPORT_MAP.get(sport_raw.lower(), "other")

    elapsed = val("total_elapsed_time") or 0
    duration_mins = round(elapsed / 60, 2)

    distance_raw = val("total_distance")
    distance_km = round(distance_raw / 1000, 3) if distance_raw else None

    avg_speed = val("avg_speed")  # m/s
    avg_pace = None
    if avg_speed and avg_speed > 0 and activity_type == "run":
        pace_secs_per_km = 1000 / avg_speed
        mins = int(pace_secs_per_km // 60)
        secs = int(pace_secs_per_km % 60)
        avg_pace = f"{mins}:{secs:02d}/km"

    return {
        "garmin_id": garmin_id,
        "type": activity_type,
        "date": date_str,
        "duration_mins": duration_mins,
        "distance_km": distance_km,
        "avg_hr": val("avg_heart_rate"),
        "avg_pace": avg_pace,
        "calories": val("total_calories"),
    }
