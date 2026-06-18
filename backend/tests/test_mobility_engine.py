from datetime import date, timedelta
from sqlmodel import Session
from models import Activity, PlanWorkout, MobilitySession, TrainingPlan, UserProfile
from services.mobility_engine import recommend_routine

def _add_activity(session, type_, distance_km, days_ago=0):
    d = date.today() - timedelta(days=days_ago)
    a = Activity(garmin_id=f"g_{type_}_{days_ago}_{d}", type=type_, date=d,
                 duration_mins=45, distance_km=distance_km)
    session.add(a)
    session.commit()
    return a

def _set_tomorrow_long_run(session):
    pw = PlanWorkout(plan_id=1, week=1, day=2, workout_type="long_run",
                     date_scheduled=date.today() + timedelta(days=1))
    session.add(pw)
    session.commit()

def test_day_after_long_run_21k(session: Session):
    profile = UserProfile(id=1, current_plan_id=1)
    plan = TrainingPlan(id=1, name="Hal Higdon 21k Novice", distance="21k", duration_weeks=12, json_structure="[]")
    session.add(plan); session.add(profile); session.commit()
    _add_activity(session, "run", distance_km=11.0, days_ago=1)
    result = recommend_routine(session, date.today())
    assert result == "Post Long Run Recovery"

def test_day_before_long_run(session: Session):
    profile = UserProfile(id=1, current_plan_id=1)
    plan = TrainingPlan(id=1, name="Hal Higdon 42k Novice", distance="42k", duration_weeks=18, json_structure="[]")
    session.add(plan); session.add(profile); session.commit()
    _set_tomorrow_long_run(session)
    result = recommend_routine(session, date.today())
    assert result == "Pre Long Run Activation"

def test_crossfit_day(session: Session):
    session.add(UserProfile(id=1)); session.commit()
    _add_activity(session, "crossfit", distance_km=None, days_ago=0)
    result = recommend_routine(session, date.today())
    assert result == "Upper Body & Thoracic Mobility"

def test_default_fallback(session: Session):
    plan = TrainingPlan(id=1, name="Test", distance="21k", duration_weeks=12, json_structure="[]")
    session.add(plan)
    session.add(UserProfile(id=1))
    # Add a non-rest workout for today so Rule 4 (rest day) doesn't fire
    session.add(PlanWorkout(plan_id=1, week=1, day=1, workout_type="easy_run",
                            date_scheduled=date.today()))
    session.commit()
    result = recommend_routine(session, date.today())
    assert result == "Running Foundation"
