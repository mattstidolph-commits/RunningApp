from datetime import date
from sqlmodel import Session
from models import Activity, TrainingPlan, PlanWorkout, MobilitySession, UserProfile

def test_activity_creation(session: Session):
    act = Activity(garmin_id="g1", type="run", date=date(2026,1,1), duration_mins=45.0, distance_km=8.0)
    session.add(act)
    session.commit()
    session.refresh(act)
    assert act.id is not None
    assert act.garmin_id == "g1"

def test_user_profile_defaults(session: Session):
    profile = UserProfile()
    session.add(profile)
    session.commit()
    assert profile.weekly_crossfit_days == 3
