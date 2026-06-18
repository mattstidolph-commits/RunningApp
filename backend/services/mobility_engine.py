from datetime import date, timedelta
from sqlmodel import Session, select
from models import Activity, PlanWorkout, UserProfile, TrainingPlan

LONG_RUN_THRESHOLDS = {"21k": 10.0, "42k": 15.0}

def recommend_routine(session: Session, today: date) -> str:
    profile = session.get(UserProfile, 1)
    plan_distance = "21k"
    if profile and profile.current_plan_id:
        plan = session.get(TrainingPlan, profile.current_plan_id)
        if plan:
            plan_distance = plan.distance

    threshold = LONG_RUN_THRESHOLDS.get(plan_distance, 10.0)
    yesterday = today - timedelta(days=1)

    # Rule 1: day after long run
    yesterday_long = session.exec(
        select(Activity).where(
            Activity.date == yesterday,
            Activity.type == "run",
            Activity.distance_km >= threshold,
        )
    ).first()
    if yesterday_long:
        return "Post Long Run Recovery"

    # Rule 2: day before long run
    tomorrow_long = session.exec(
        select(PlanWorkout).where(
            PlanWorkout.workout_type == "long_run",
            PlanWorkout.date_scheduled == today + timedelta(days=1),
        )
    ).first()
    if tomorrow_long:
        return "Pre Long Run Activation"

    # Rule 3: CrossFit today
    crossfit_today = session.exec(
        select(Activity).where(Activity.date == today, Activity.type == "crossfit")
    ).first()
    if crossfit_today:
        return "Upper Body & Thoracic Mobility"

    # Rule 4: rest day + no runs this week
    week_start = today - timedelta(days=today.weekday())
    runs_this_week = session.exec(
        select(Activity).where(
            Activity.date >= week_start,
            Activity.type == "run",
        )
    ).first()
    today_pw = session.exec(
        select(PlanWorkout).where(PlanWorkout.date_scheduled == today)
    ).first()
    is_rest_day = not today_pw or today_pw.workout_type == "rest"
    if is_rest_day and not runs_this_week:
        return "Full Body Flexibility"

    # Rule 5: default
    return "Running Foundation"
