from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import Activity

router = APIRouter()

@router.get("/charts")
def get_charts(session: Session = Depends(get_session)):
    since = date.today() - timedelta(weeks=12)
    activities = session.exec(
        select(Activity).where(Activity.date >= since).order_by(Activity.date)
    ).all()

    pace_trend = []
    for a in activities:
        if a.type == "run" and a.avg_pace:
            parts = a.avg_pace.replace("/km", "").split(":")
            if len(parts) == 2:
                pace_secs = int(parts[0]) * 60 + int(parts[1])
                pace_trend.append({"date": str(a.date), "pace_secs": pace_secs, "pace_label": a.avg_pace})

    weekly: dict[str, dict] = {}
    for a in activities:
        week_start = a.date - timedelta(days=a.date.weekday())
        key = str(week_start)
        if key not in weekly:
            weekly[key] = {"week": key, "run_km": 0.0, "crossfit_count": 0}
        if a.type == "run":
            weekly[key]["run_km"] += a.distance_km or 0
        elif a.type == "crossfit":
            weekly[key]["crossfit_count"] += 1
    weekly_mileage = sorted(weekly.values(), key=lambda x: x["week"])

    hr_trend = [
        {"date": str(a.date), "avg_hr": a.avg_hr}
        for a in activities if a.avg_hr
    ]

    return {
        "pace_trend": pace_trend,
        "weekly_mileage": weekly_mileage,
        "hr_trend": hr_trend,
    }
