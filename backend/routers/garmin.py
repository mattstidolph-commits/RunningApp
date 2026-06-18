from fastapi import APIRouter

router = APIRouter()

@router.post("/sync")
def sync_garmin():
    return {
        "status": "not_configured",
        "message": "Automated Garmin sync coming in Phase 2. Use FIT file upload on the Progress page.",
    }
