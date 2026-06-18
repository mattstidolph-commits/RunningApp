from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routers import activities, plans, mobility, dashboard, progress, garmin

app = FastAPI(title="Running App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(activities.router, prefix="/activities", tags=["activities"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
app.include_router(mobility.router, prefix="/mobility", tags=["mobility"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(progress.router, prefix="/progress", tags=["progress"])
app.include_router(garmin.router, prefix="/garmin", tags=["garmin"])
