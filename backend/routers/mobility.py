import json
import os
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from database import get_session
from models import MobilitySession
from services.mobility_engine import recommend_routine

router = APIRouter()

ROUTINES_PATH = os.path.join(os.path.dirname(__file__), "..", "mobility_routines.json")

def _load_routines() -> list[dict]:
    with open(ROUTINES_PATH) as f:
        return json.load(f)

@router.get("/routines")
def get_routines(area: Optional[str] = None):
    routines = _load_routines()
    if area:
        routines = [r for r in routines if area.lower() in [a.lower() for a in r["areas"]]]
    return routines

@router.get("/recommendation")
def get_recommendation(session: Session = Depends(get_session)):
    routine_name = recommend_routine(session, date.today())
    routines = _load_routines()
    routine = next((r for r in routines if r["name"] == routine_name), None)
    return {"routine_name": routine_name, "routine": routine}

class SessionCreate(BaseModel):
    routine_name: str
    duration_mins: int
    notes: Optional[str] = None
    recommended: bool = False
    date: Optional[date] = None

@router.post("/sessions", response_model=MobilitySession)
def log_session(body: SessionCreate, session: Session = Depends(get_session)):
    ms = MobilitySession(
        date=body.date or date.today(),
        routine_name=body.routine_name,
        duration_mins=body.duration_mins,
        notes=body.notes,
        completed=True,
        recommended=body.recommended,
    )
    session.add(ms)
    session.commit()
    session.refresh(ms)
    return ms

@router.get("/sessions", response_model=list[MobilitySession])
def get_sessions(days: int = 30, session: Session = Depends(get_session)):
    since = date.today() - timedelta(days=days)
    return session.exec(
        select(MobilitySession)
        .where(MobilitySession.date >= since)
        .order_by(MobilitySession.date.desc())
    ).all()
