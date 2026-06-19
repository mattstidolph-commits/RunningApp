import os
import pathlib
from requests import HTTPError
from garminconnect import Garmin

TOKEN_DIR = ".garmintoken"

SPORT_MAP = {
    "running": "run",
    "cardio": "crossfit",
    "strength_training": "crossfit",
    "walking": "walk",
}


def _get_client() -> Garmin:
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")
    if not email or not password:
        raise RuntimeError("GARMIN_EMAIL and GARMIN_PASSWORD must be set in .env")

    api = Garmin(email, password)
    token_path = pathlib.Path(TOKEN_DIR)
    token_exists = token_path.exists() and any(token_path.iterdir())

    if token_exists:
        try:
            api.login(TOKEN_DIR)
            return api
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 429:
                raise RuntimeError(
                    "Garmin is rate-limiting requests. Please wait a few minutes before syncing again."
                ) from e
            # Token is invalid/expired — fall through to full login
        except Exception:
            pass  # Token unreadable — fall through to full login

    try:
        api.login()
    except HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            raise RuntimeError(
                "Garmin is rate-limiting requests. Please wait a few minutes before syncing again."
            ) from e
        raise
    api.garth.dump(TOKEN_DIR)
    return api


def _map_activity(a: dict) -> dict:
    type_key = (a.get("activityType") or {}).get("typeKey", "other")
    activity_type = SPORT_MAP.get(type_key, "other")

    speed = a.get("averageSpeed")
    avg_pace = None
    if speed and speed > 0 and activity_type == "run":
        pace_secs = 1000 / speed
        mins = int(pace_secs // 60)
        secs = int(pace_secs % 60)
        avg_pace = f"{mins}:{secs:02d}/km"

    distance_raw = a.get("distance")
    return {
        "garmin_id": str(a["activityId"]),
        "type": activity_type,
        "date": a["startTimeLocal"][:10],
        "duration_mins": round(a["duration"] / 60, 2),
        "distance_km": round(distance_raw / 1000, 3) if distance_raw else None,
        "avg_hr": a.get("averageHR"),
        "avg_pace": avg_pace,
        "calories": a.get("calories"),
    }


def fetch_recent_activities(limit: int = 20) -> list[dict]:
    api = _get_client()
    raw = api.get_activities(0, limit)
    return [_map_activity(a) for a in raw]
