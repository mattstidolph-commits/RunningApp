from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from database import get_session
from models import PlanWorkout, TrainingPlan, UserProfile
from services.plan_scheduler import schedule_plan

router = APIRouter()

class ActivateRequest(BaseModel):
    start_date: date

class WorkoutUpdate(BaseModel):
    workout_type: Optional[str] = None
    target_distance_km: Optional[float] = None
    target_duration_mins: Optional[int] = None
    notes: Optional[str] = None
    date_adjusted: Optional[date] = None
    completed_activity_id: Optional[int] = None

@router.get("", response_model=list[TrainingPlan])
def get_plans(session: Session = Depends(get_session)):
    return session.exec(select(TrainingPlan)).all()

@router.post("/{plan_id}/activate")
def activate_plan(plan_id: int, body: ActivateRequest, session: Session = Depends(get_session)):
    plan = session.get(TrainingPlan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    existing = session.exec(select(PlanWorkout).where(PlanWorkout.plan_id == plan_id)).all()
    for w in existing:
        session.delete(w)
    rows = schedule_plan(plan.json_structure, body.start_date)
    for r in rows:
        session.add(PlanWorkout(plan_id=plan_id, **r))
    profile = session.get(UserProfile, 1) or UserProfile(id=1)
    profile.current_plan_id = plan_id
    profile.plan_start_date = body.start_date
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

@router.get("/workouts", response_model=list[PlanWorkout])
def get_workouts(session: Session = Depends(get_session)):
    return session.exec(select(PlanWorkout).order_by(PlanWorkout.date_scheduled)).all()

@router.get("/workouts/today", response_model=Optional[PlanWorkout])
def get_today_workout(session: Session = Depends(get_session)):
    return session.exec(
        select(PlanWorkout).where(PlanWorkout.date_scheduled == date.today())
    ).first()

@router.put("/workouts/{workout_id}", response_model=PlanWorkout)
def update_workout(workout_id: int, body: WorkoutUpdate, session: Session = Depends(get_session)):
    pw = session.get(PlanWorkout, workout_id)
    if not pw:
        raise HTTPException(404, "Workout not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(pw, field, value)
    session.add(pw)
    session.commit()
    session.refresh(pw)
    return pw
