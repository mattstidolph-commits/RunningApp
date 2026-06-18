import os
import tempfile
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select
from database import get_session
from models import Activity
from services.fit_parser import parse_fit_file

router = APIRouter()

@router.get("", response_model=list[Activity])
def get_activities(session: Session = Depends(get_session)):
    return session.exec(select(Activity).order_by(Activity.date.desc())).all()

@router.post("/upload-fit", response_model=Activity)
def upload_fit(file: UploadFile = File(...), session: Session = Depends(get_session)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fit") as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    try:
        parsed = parse_fit_file(tmp_path)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or unreadable FIT file")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    existing = session.exec(
        select(Activity).where(Activity.garmin_id == parsed["garmin_id"])
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Activity already imported")

    from datetime import date
    parsed["date"] = date.fromisoformat(parsed["date"])
    activity = Activity(**parsed)
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity
