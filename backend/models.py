from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel

class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    garmin_id: str = Field(unique=True, index=True)
    type: str                          # run | crossfit | walk | other
    date: date
    duration_mins: float
    distance_km: Optional[float] = None
    avg_hr: Optional[int] = None
    avg_pace: Optional[str] = None     # "5:30/km"
    calories: Optional[int] = None
    raw_fit_path: Optional[str] = None

class TrainingPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    distance: str                      # "21k" | "42k"
    duration_weeks: int
    json_structure: str                # JSON string

class PlanWorkout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: int = Field(foreign_key="trainingplan.id")
    week: int
    day: int                           # 1=Mon … 7=Sun
    workout_type: str
    target_distance_km: Optional[float] = None
    target_duration_mins: Optional[int] = None
    notes: Optional[str] = None
    completed_activity_id: Optional[int] = Field(default=None, foreign_key="activity.id")
    date_scheduled: Optional[date] = None
    date_adjusted: Optional[date] = None

class MobilitySession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    routine_name: str
    duration_mins: int
    notes: Optional[str] = None
    completed: bool = False
    recommended: bool = False

class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = ""
    target_race: Optional[str] = None
    target_race_date: Optional[date] = None
    garmin_email: Optional[str] = None
    weekly_crossfit_days: int = 3
    current_plan_id: Optional[int] = Field(default=None, foreign_key="trainingplan.id")
    plan_start_date: Optional[date] = None
