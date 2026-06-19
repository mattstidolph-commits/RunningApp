from datetime import date
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import Activity
from services.garmin_client import fetch_recent_activities

router = APIRouter()


@router.post("/sync")
def sync_garmin(session: Session = Depends(get_session)):
    try:
        activities = fetch_recent_activities()
    except RuntimeError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Garmin login failed: {e}"}

    synced = 0
    skipped = 0
    for parsed in activities:
        existing = session.exec(
            select(Activity).where(Activity.garmin_id == parsed["garmin_id"])
        ).first()
        if existing:
            skipped += 1
            continue
        parsed["date"] = date.fromisoformat(parsed["date"])
        session.add(Activity(**parsed))
        synced += 1

    session.commit()
    return {
        "status": "ok",
        "synced": synced,
        "skipped": skipped,
        "message": f"Synced {synced} new {'activity' if synced == 1 else 'activities'}, {skipped} already imported.",
    }
