from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import Activity, PlanWorkout, UserProfile
from services.mobility_engine import recommend_routine

router = APIRouter()

@router.get("")
def get_dashboard(session: Session = Depends(get_session)):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    today_workout = session.exec(
        select(PlanWorkout).where(PlanWorkout.date_scheduled == today)
    ).first()

    last_activity = session.exec(
        select(Activity).order_by(Activity.date.desc())
    ).first()

    week_activities = session.exec(
        select(Activity).where(Activity.date >= week_start)
    ).all()
    week_runs = [a for a in week_activities if a.type == "run"]
    week_crossfit = [a for a in week_activities if a.type == "crossfit"]
    total_km = sum(a.distance_km or 0 for a in week_runs)

    week_planned = session.exec(
        select(PlanWorkout).where(
            PlanWorkout.date_scheduled >= week_start,
            PlanWorkout.date_scheduled <= today,
            PlanWorkout.workout_type != "rest",
        )
    ).all()
    completed_count = sum(1 for w in week_planned if w.completed_activity_id is not None)

    routine_name = recommend_routine(session, today)

    return {
        "today_workout": today_workout,
        "last_activity": last_activity,
        "recommended_mobility": routine_name,
        "weekly_stats": {
            "km_this_week": round(total_km, 1),
            "crossfit_sessions": len(week_crossfit),
            "workouts_completed": completed_count,
            "workouts_planned": len(week_planned),
        },
    }
