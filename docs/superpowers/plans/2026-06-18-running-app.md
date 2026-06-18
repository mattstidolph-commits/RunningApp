# Running App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local running training dashboard that ingests Garmin data, tracks structured training plans, and recommends mobility work.

**Architecture:** Python FastAPI backend on port 8000, React/Vite frontend on port 5173, SQLite via SQLModel. All data lives locally — no cloud dependencies. Two terminal windows to run the app.

**Tech Stack:** Python 3.11+, FastAPI, SQLModel, fitparse, garminconnect, React 18, Vite, Recharts, FullCalendar, Tailwind CSS, pytest, Axios

## Global Constraints

- Python 3.11+; Node 18+
- Backend runs on port 8000; frontend on port 5173
- SQLite file at `backend/running.db`; created automatically on first run
- All dates stored as ISO strings (`YYYY-MM-DD`)
- CORS enabled for `http://localhost:5173`
- No cloud calls; no authentication required
- Workout types enum: `easy_run`, `long_run`, `tempo`, `intervals`, `rest`, `cross_train`
- Activity types enum: `run`, `crossfit`, `walk`, `other`

---

## File Map

```
backend/
  main.py                        # FastAPI app, CORS, router registration
  database.py                    # Engine, session, create_db_and_tables()
  models.py                      # SQLModel table definitions (all 5 entities)
  requirements.txt
  seed_data.py                   # One-off script: seed plans + mobility routines
  routers/
    activities.py                # GET /activities, POST /activities/upload-fit
    plans.py                     # GET /plans, GET/PUT plan-workouts, POST activate
    mobility.py                  # GET routines, GET recommendation, GET/POST sessions
    dashboard.py                 # GET /dashboard
    progress.py                  # GET /progress/charts
    garmin.py                    # POST /garmin/sync (Phase 2 scaffold)
  services/
    fit_parser.py                # parse_fit_file(path) -> dict
    mobility_engine.py           # recommend_routine(db, today) -> str
    plan_scheduler.py            # schedule_plan(plan, start_date) -> list[dict]
  tests/
    conftest.py                  # in-memory DB fixture
    test_fit_parser.py
    test_mobility_engine.py
    test_plan_scheduler.py
    test_routes.py
frontend/
  package.json
  vite.config.js
  tailwind.config.js
  postcss.config.js
  index.html
  src/
    main.jsx
    App.jsx                      # React Router shell + nav
    api.js                       # Axios client + all API call functions
    pages/
      Dashboard.jsx
      Calendar.jsx
      TrainingPlan.jsx
      Mobility.jsx
      Progress.jsx
    components/
      WorkoutCard.jsx
      MobilityCard.jsx
      ActivitySummary.jsx
      WeeklySnapshot.jsx
      FitUpload.jsx
      PaceChart.jsx
      MileageChart.jsx
      LoadChart.jsx
      RoutineCard.jsx
      WorkoutEditor.jsx
```

---

### Task 1: Backend scaffold

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/database.py`

**Interfaces:**
- Produces: `get_session()` dependency used by all routers; `create_db_and_tables()` called at startup

- [ ] **Step 1: Create `backend/requirements.txt`**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlmodel==0.0.19
fitparse==1.2.0
garminconnect==0.2.18
python-multipart==0.0.9
pytest==8.2.0
pytest-asyncio==0.23.7
httpx==0.27.0
```

- [ ] **Step 2: Install dependencies**

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Expected: all packages install without error.

- [ ] **Step 3: Create `backend/database.py`**

```python
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./running.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

- [ ] **Step 4: Create `backend/main.py`**

```python
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
```

- [ ] **Step 5: Create empty router stubs so main.py imports don't fail**

Create `backend/routers/__init__.py` (empty).

Create `backend/routers/activities.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

Repeat the same two-liner stub for `plans.py`, `mobility.py`, `dashboard.py`, `progress.py`, `garmin.py`.

- [ ] **Step 6: Verify server starts**

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Expected: `Application startup complete.` Open `http://localhost:8000/docs` — see empty Swagger UI. Stop with Ctrl+C.

- [ ] **Step 7: Commit**

```bash
git add backend/
git commit -m "feat: backend scaffold — FastAPI app, database setup, empty routers"
```

---

### Task 2: SQLModel models

**Files:**
- Create: `backend/models.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/__init__.py`

**Interfaces:**
- Produces: `Activity`, `TrainingPlan`, `PlanWorkout`, `MobilitySession`, `UserProfile` — imported by all routers and services

- [ ] **Step 1: Create `backend/models.py`**

```python
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
```

- [ ] **Step 2: Create `backend/tests/conftest.py`**

```python
import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    from main import app
    from database import get_session
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
```

- [ ] **Step 3: Create `backend/tests/__init__.py`** (empty)

- [ ] **Step 4: Write model smoke test `backend/tests/test_models.py`**

```python
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
```

- [ ] **Step 5: Run tests**

```bash
cd backend
pytest tests/test_models.py -v
```

Expected: 2 passed.

- [ ] **Step 6: Commit**

```bash
git add backend/models.py backend/tests/
git commit -m "feat: SQLModel table definitions and test fixtures"
```

---

### Task 3: Seed data — training plans + mobility routines

**Files:**
- Create: `backend/seed_data.py`

**Interfaces:**
- Produces: rows in `training_plans` table; `MobilitySession` routines loaded from embedded JSON in `seed_data.py`

- [ ] **Step 1: Create `backend/seed_data.py`**

```python
"""Run once: python seed_data.py"""
import json
from datetime import date
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import TrainingPlan, UserProfile

create_db_and_tables()

def make_week(week, easy_runs, long_km, has_tempo=False, tempo_km=None):
    """Build a standard Mon/Wed/Fri easy + Sun long week. Tue=XT, Thu=rest, Sat=rest."""
    days = []
    for day, km in [(1, easy_runs[0]), (3, easy_runs[1]), (5, easy_runs[2])]:
        wtype = "tempo" if has_tempo and day == 3 else "easy_run"
        d_km = tempo_km if has_tempo and day == 3 else km
        days.append({"day": day, "workout_type": wtype,
                     "target_distance_km": d_km, "notes": "Easy comfortable pace" if wtype == "easy_run" else "Comfortably hard, 10k race pace"})
    days.append({"day": 2, "workout_type": "cross_train", "target_distance_km": None, "notes": "CrossFit or cycling — no running"})
    days.append({"day": 4, "workout_type": "rest", "target_distance_km": None, "notes": "Rest or gentle walk"})
    days.append({"day": 6, "workout_type": "rest", "target_distance_km": None, "notes": "Rest — prepare for long run"})
    days.append({"day": 7, "workout_type": "long_run", "target_distance_km": long_km, "notes": "Easy pace, conversational throughout"})
    return {"week": week, "days": sorted(days, key=lambda d: d["day"])}

plans = [
    {
        "name": "Hal Higdon 21k Novice",
        "distance": "21k",
        "duration_weeks": 12,
        "weeks": [
            make_week(1,  [5,5,5],   10),
            make_week(2,  [5,6,5],   11),
            make_week(3,  [6,6,6],   13),
            make_week(4,  [6,8,6],   11),   # step-back
            make_week(5,  [6,8,6],   14),
            make_week(6,  [8,8,8],   16),
            make_week(7,  [8,8,8],   14),   # step-back
            make_week(8,  [8,10,8],  18),
            make_week(9,  [8,10,8],  16),   # step-back
            make_week(10, [10,10,10],19),
            make_week(11, [8,6,5],   11),   # taper
            {"week": 12, "days": [
                {"day": 1, "workout_type": "easy_run",  "target_distance_km": 5,  "notes": "Easy shakeout"},
                {"day": 2, "workout_type": "rest",       "target_distance_km": None,"notes": "Rest"},
                {"day": 3, "workout_type": "easy_run",  "target_distance_km": 3,  "notes": "Short and easy"},
                {"day": 4, "workout_type": "rest",       "target_distance_km": None,"notes": "Rest"},
                {"day": 5, "workout_type": "rest",       "target_distance_km": None,"notes": "Rest — race tomorrow"},
                {"day": 6, "workout_type": "rest",       "target_distance_km": None,"notes": "Rest"},
                {"day": 7, "workout_type": "long_run",  "target_distance_km": 21, "notes": "RACE DAY — run your race!"},
            ]},
        ],
    },
    {
        "name": "Hal Higdon 42k Novice",
        "distance": "42k",
        "duration_weeks": 18,
        "weeks": [
            make_week(1,  [5,5,5],   10),
            make_week(2,  [5,5,5],   11),
            make_week(3,  [6,6,6],   13),
            make_week(4,  [5,5,5],   11),   # step-back
            make_week(5,  [6,6,6],   16),
            make_week(6,  [6,6,6],   18),
            make_week(7,  [6,6,6],   16),   # step-back
            make_week(8,  [6,6,6],   21),
            make_week(9,  [8,8,8],   18),   # step-back
            make_week(10, [8,8,8],   26),
            make_week(11, [8,8,8],   24),   # step-back
            make_week(12, [10,10,10],29),
            make_week(13, [8,8,8],   24),   # step-back
            make_week(14, [10,10,10],32),
            make_week(15, [8,8,8],   29),   # step-back
            make_week(16, [10,10,10],32),   # peak
            make_week(17, [8,6,5],   19),   # taper
            {"week": 18, "days": [
                {"day": 1, "workout_type": "easy_run", "target_distance_km": 5,  "notes": "Easy shakeout"},
                {"day": 2, "workout_type": "rest",      "target_distance_km": None,"notes": "Rest"},
                {"day": 3, "workout_type": "easy_run", "target_distance_km": 3,  "notes": "Short and easy"},
                {"day": 4, "workout_type": "rest",      "target_distance_km": None,"notes": "Rest"},
                {"day": 5, "workout_type": "rest",      "target_distance_km": None,"notes": "Rest — race tomorrow"},
                {"day": 6, "workout_type": "rest",      "target_distance_km": None,"notes": "Rest"},
                {"day": 7, "workout_type": "long_run", "target_distance_km": 42, "notes": "RACE DAY — you've got this!"},
            ]},
        ],
    },
    {
        "name": "Hal Higdon 42k Intermediate",
        "distance": "42k",
        "duration_weeks": 18,
        "weeks": [
            make_week(1,  [6,6,6],   13, has_tempo=True, tempo_km=6),
            make_week(2,  [6,6,6],   14, has_tempo=True, tempo_km=6),
            make_week(3,  [8,8,8],   16, has_tempo=True, tempo_km=8),
            make_week(4,  [6,6,6],   13, has_tempo=True, tempo_km=6),   # step-back
            make_week(5,  [8,8,8],   18, has_tempo=True, tempo_km=8),
            make_week(6,  [8,8,8],   21, has_tempo=True, tempo_km=8),
            make_week(7,  [8,8,8],   18, has_tempo=True, tempo_km=8),   # step-back
            make_week(8,  [10,10,10],24, has_tempo=True, tempo_km=10),
            make_week(9,  [8,8,8],   21, has_tempo=True, tempo_km=8),   # step-back
            make_week(10, [10,10,10],27, has_tempo=True, tempo_km=10),
            make_week(11, [10,10,10],24, has_tempo=True, tempo_km=10),  # step-back
            make_week(12, [10,10,10],32, has_tempo=True, tempo_km=10),
            make_week(13, [10,10,10],27, has_tempo=True, tempo_km=10),  # step-back
            make_week(14, [10,10,10],32, has_tempo=True, tempo_km=10),
            make_week(15, [10,10,10],29, has_tempo=True, tempo_km=10),  # step-back
            make_week(16, [10,10,10],32, has_tempo=True, tempo_km=10),  # peak
            make_week(17, [8,6,5],   19),                                # taper
            {"week": 18, "days": [
                {"day": 1, "workout_type": "easy_run", "target_distance_km": 5,  "notes": "Easy shakeout"},
                {"day": 2, "workout_type": "rest",      "target_distance_km": None,"notes": "Rest"},
                {"day": 3, "workout_type": "easy_run", "target_distance_km": 3,  "notes": "Short and easy"},
                {"day": 4, "workout_type": "rest",      "target_distance_km": None,"notes": "Rest"},
                {"day": 5, "workout_type": "rest",      "target_distance_km": None,"notes": "Rest"},
                {"day": 6, "workout_type": "rest",      "target_distance_km": None,"notes": "Rest"},
                {"day": 7, "workout_type": "long_run", "target_distance_km": 42, "notes": "RACE DAY"},
            ]},
        ],
    },
]

MOBILITY_ROUTINES = [
    {"name": "Post Long Run Recovery", "areas": ["hips", "calves", "hamstrings"], "duration_mins": 15,
     "exercises": [
         {"name": "Hip Flexor Stretch", "duration_secs": 60, "cue": "Lunge, drive hips forward gently"},
         {"name": "Standing Calf Stretch", "duration_secs": 45, "cue": "Lean into wall, heel flat"},
         {"name": "Supine Hamstring Stretch", "duration_secs": 60, "cue": "Lie on back, pull leg toward chest"},
         {"name": "Figure Four Glute Stretch", "duration_secs": 60, "cue": "Cross ankle over opposite knee"},
         {"name": "Foam Roll IT Band", "duration_secs": 90, "cue": "Slow rolls, pause on tight spots"},
         {"name": "Downward Dog Calf Pedal", "duration_secs": 60, "cue": "Alternate pressing heels to floor"},
     ]},
    {"name": "Pre Long Run Activation", "areas": ["glutes", "ankles"], "duration_mins": 10,
     "exercises": [
         {"name": "Glute Bridge", "duration_secs": 45, "cue": "Drive hips up, squeeze glutes at top"},
         {"name": "Clamshells", "duration_secs": 45, "cue": "Keep pelvis still, rotate knee up"},
         {"name": "Ankle Circles", "duration_secs": 30, "cue": "Full range, both directions"},
         {"name": "Leg Swings Front-Back", "duration_secs": 30, "cue": "Hold wall, swing freely"},
         {"name": "Leg Swings Side-Side", "duration_secs": 30, "cue": "Cross body, controlled"},
         {"name": "High Knees March", "duration_secs": 30, "cue": "Exaggerated knee lift, tall posture"},
     ]},
    {"name": "Upper Body & Thoracic Mobility", "areas": ["shoulders", "thoracic"], "duration_mins": 12,
     "exercises": [
         {"name": "Thoracic Extension over Foam Roller", "duration_secs": 60, "cue": "Roll between shoulder blades, arms crossed"},
         {"name": "Thread the Needle", "duration_secs": 45, "cue": "From all-fours, slide arm under body"},
         {"name": "Doorway Chest Stretch", "duration_secs": 45, "cue": "Arms at 90°, lean gently forward"},
         {"name": "Cat-Cow", "duration_secs": 45, "cue": "Slow and controlled, full range"},
         {"name": "Shoulder Circles", "duration_secs": 30, "cue": "Large circles, both directions"},
         {"name": "Chin Tucks", "duration_secs": 30, "cue": "Pull chin straight back, hold 2 sec"},
     ]},
    {"name": "Full Body Flexibility", "areas": ["full_body"], "duration_mins": 30,
     "exercises": [
         {"name": "Child's Pose", "duration_secs": 60, "cue": "Reach arms forward, breathe into back"},
         {"name": "Hip Flexor Stretch", "duration_secs": 60, "cue": "Deep lunge, front knee over ankle"},
         {"name": "Seated Forward Fold", "duration_secs": 60, "cue": "Hinge at hips, soft knees"},
         {"name": "Pigeon Pose", "duration_secs": 90, "cue": "Square hips, breathe through discomfort"},
         {"name": "Supine Twist", "duration_secs": 60, "cue": "Shoulders flat, look away from knees"},
         {"name": "Standing Side Stretch", "duration_secs": 30, "cue": "Arm overhead, lean to opposite side"},
         {"name": "Doorway Chest Stretch", "duration_secs": 45, "cue": "Arms at 90°"},
         {"name": "Calf Stretch", "duration_secs": 45, "cue": "Straight leg then bent knee version"},
         {"name": "Ankle Circles", "duration_secs": 30, "cue": "Full range both directions"},
     ]},
    {"name": "Running Foundation", "areas": ["calves", "hips", "ankles"], "duration_mins": 10,
     "exercises": [
         {"name": "Standing Calf Raise", "duration_secs": 30, "cue": "Slow up, controlled down"},
         {"name": "Hip Flexor Stretch", "duration_secs": 45, "cue": "Lunge position, tall spine"},
         {"name": "Ankle Alphabet", "duration_secs": 30, "cue": "Trace A-Z with your big toe"},
         {"name": "Single-Leg Balance", "duration_secs": 30, "cue": "Eyes open then closed"},
         {"name": "Calf Stretch", "duration_secs": 45, "cue": "Against wall, straight leg"},
         {"name": "Hip Circle", "duration_secs": 30, "cue": "Hands on hips, large slow circles"},
     ]},
    {"name": "Hip Opening Flow", "areas": ["hips"], "duration_mins": 15,
     "exercises": [
         {"name": "Deep Squat Hold", "duration_secs": 60, "cue": "Heels flat, elbows push knees out"},
         {"name": "Pigeon Pose Left", "duration_secs": 90, "cue": "Square hips forward"},
         {"name": "Pigeon Pose Right", "duration_secs": 90, "cue": "Square hips forward"},
         {"name": "Lateral Lunge", "duration_secs": 45, "cue": "Sit into hip, keep chest up"},
         {"name": "Figure Four Stretch", "duration_secs": 60, "cue": "Ankle over opposite knee, flex foot"},
         {"name": "Fire Hydrant", "duration_secs": 30, "cue": "From all-fours, lift knee to side"},
     ]},
    {"name": "Ankle & Foot Care", "areas": ["ankles"], "duration_mins": 10,
     "exercises": [
         {"name": "Ankle Circles", "duration_secs": 45, "cue": "Seated, full range both directions"},
         {"name": "Towel Scrunches", "duration_secs": 30, "cue": "Scrunch towel with toes, 10 reps"},
         {"name": "Heel Raises", "duration_secs": 45, "cue": "Slow 3-count up and down"},
         {"name": "Toe Spread", "duration_secs": 30, "cue": "Spread toes wide, hold 5 sec"},
         {"name": "Single-Leg Calf Raise", "duration_secs": 45, "cue": "Off step edge, full range"},
         {"name": "Peroneal Stretch", "duration_secs": 45, "cue": "Foot inverted, feel outside of ankle"},
     ]},
    {"name": "Morning Wake-Up", "areas": ["full_body"], "duration_mins": 8,
     "exercises": [
         {"name": "Cat-Cow", "duration_secs": 45, "cue": "Breathe slowly, wake up the spine"},
         {"name": "Child's Pose", "duration_secs": 30, "cue": "Arms long, breathe into back"},
         {"name": "Hip Circles Standing", "duration_secs": 30, "cue": "Hands on hips, big slow circles"},
         {"name": "Arm Swings", "duration_secs": 20, "cue": "Across body and out wide"},
         {"name": "Leg Swings", "duration_secs": 20, "cue": "Hold wall, swing forward and back"},
         {"name": "Gentle Neck Rolls", "duration_secs": 20, "cue": "Half circles, ear to shoulder"},
     ]},
]

def seed():
    with Session(engine) as session:
        for p in plans:
            existing = session.exec(
                __import__("sqlmodel").select(TrainingPlan).where(TrainingPlan.name == p["name"])
            ).first()
            if existing:
                print(f"  skip (exists): {p['name']}")
                continue
            weeks = p.pop("weeks")
            tp = TrainingPlan(json_structure=json.dumps(weeks), **p)
            session.add(tp)
            print(f"  seeded: {tp.name}")

        existing_profile = session.get(UserProfile, 1)
        if not existing_profile:
            session.add(UserProfile(id=1))

        session.commit()

    import os, json as _json
    routines_path = os.path.join(os.path.dirname(__file__), "mobility_routines.json")
    with open(routines_path, "w") as f:
        _json.dump(MOBILITY_ROUTINES, f, indent=2)
    print(f"  wrote mobility_routines.json ({len(MOBILITY_ROUTINES)} routines)")

if __name__ == "__main__":
    seed()
    print("Seed complete.")
```

- [ ] **Step 2: Run seed script**

```bash
cd backend
python seed_data.py
```

Expected output:
```
  seeded: Hal Higdon 21k Novice
  seeded: Hal Higdon 42k Novice
  seeded: Hal Higdon 42k Intermediate
  wrote mobility_routines.json (8 routines)
Seed complete.
```

- [ ] **Step 3: Verify DB**

```bash
python -c "from sqlmodel import Session, select; from database import engine; from models import TrainingPlan; s=Session(engine); print([p.name for p in s.exec(select(TrainingPlan)).all()])"
```

Expected: `['Hal Higdon 21k Novice', 'Hal Higdon 42k Novice', 'Hal Higdon 42k Intermediate']`

- [ ] **Step 4: Commit**

```bash
git add backend/seed_data.py backend/mobility_routines.json
git commit -m "feat: seed training plans and mobility routines"
```

---

### Task 4: FIT file parser service

**Files:**
- Create: `backend/services/__init__.py` (empty)
- Create: `backend/services/fit_parser.py`
- Create: `backend/tests/test_fit_parser.py`

**Interfaces:**
- Produces: `parse_fit_file(path: str) -> dict` returning keys: `garmin_id`, `type`, `date`, `duration_mins`, `distance_km`, `avg_hr`, `avg_pace`, `calories`

- [ ] **Step 1: Write failing test `backend/tests/test_fit_parser.py`**

```python
import pytest
from unittest.mock import patch, MagicMock
from services.fit_parser import parse_fit_file
from datetime import datetime, timezone

def make_mock_record(field_map: dict):
    rec = MagicMock()
    def get_value(name):
        return field_map.get(name)
    rec.get_value = get_value
    rec.name = "record"
    return rec

def make_mock_session(field_map: dict):
    rec = MagicMock()
    def get_value(name):
        return field_map.get(name)
    rec.get_value = get_value
    rec.name = "session"
    return rec

def test_parse_run_fit_file(tmp_path):
    start_time = datetime(2026, 6, 1, 7, 0, 0, tzinfo=timezone.utc)
    session_msg = make_mock_session({
        "start_time": start_time,
        "total_elapsed_time": 2700.0,   # 45 mins
        "total_distance": 8000.0,       # 8 km in metres
        "avg_heart_rate": 148,
        "total_calories": 520,
        "sport": "running",
        "avg_speed": 2.96,              # m/s ≈ 5:38/km
    })
    with patch("services.fit_parser.fitparse.FitFile") as MockFit:
        MockFit.return_value.get_messages.return_value = [session_msg]
        result = parse_fit_file(str(tmp_path / "test.fit"))

    assert result["type"] == "run"
    assert result["duration_mins"] == pytest.approx(45.0, abs=0.1)
    assert result["distance_km"] == pytest.approx(8.0, abs=0.1)
    assert result["avg_hr"] == 148
    assert result["calories"] == 520
    assert result["date"] == "2026-06-01"
    assert "garmin_id" in result

def test_parse_crossfit_fit_file(tmp_path):
    start_time = datetime(2026, 6, 2, 9, 0, 0, tzinfo=timezone.utc)
    session_msg = make_mock_session({
        "start_time": start_time,
        "total_elapsed_time": 3600.0,
        "total_distance": None,
        "avg_heart_rate": 160,
        "total_calories": 450,
        "sport": "training",
        "avg_speed": None,
    })
    with patch("services.fit_parser.fitparse.FitFile") as MockFit:
        MockFit.return_value.get_messages.return_value = [session_msg]
        result = parse_fit_file(str(tmp_path / "cf.fit"))

    assert result["type"] == "crossfit"
    assert result["distance_km"] is None
    assert result["avg_pace"] is None
```

- [ ] **Step 2: Run to verify failure**

```bash
cd backend
pytest tests/test_fit_parser.py -v
```

Expected: `ModuleNotFoundError: No module named 'services.fit_parser'`

- [ ] **Step 3: Create `backend/services/fit_parser.py`**

```python
import fitparse
from datetime import timezone

SPORT_MAP = {
    "running": "run",
    "cycling": "other",
    "training": "crossfit",
    "walking": "walk",
}

def parse_fit_file(path: str) -> dict:
    fit = fitparse.FitFile(path)
    session = next(fit.get_messages("session"), None)
    if session is None:
        raise ValueError(f"No session message found in {path}")

    def val(name):
        return session.get_value(name)

    start_time = val("start_time")
    if hasattr(start_time, "replace"):
        date_str = start_time.strftime("%Y-%m-%d")
        garmin_id = start_time.strftime("%Y%m%d%H%M%S")
    else:
        date_str = str(start_time)[:10]
        garmin_id = str(start_time).replace("-", "").replace(":", "").replace(" ", "")

    sport_raw = val("sport") or "other"
    activity_type = SPORT_MAP.get(sport_raw.lower(), "other")

    elapsed = val("total_elapsed_time") or 0
    duration_mins = round(elapsed / 60, 2)

    distance_raw = val("total_distance")
    distance_km = round(distance_raw / 1000, 3) if distance_raw else None

    avg_speed = val("avg_speed")  # m/s
    avg_pace = None
    if avg_speed and avg_speed > 0 and activity_type == "run":
        pace_secs_per_km = 1000 / avg_speed
        mins = int(pace_secs_per_km // 60)
        secs = int(pace_secs_per_km % 60)
        avg_pace = f"{mins}:{secs:02d}/km"

    return {
        "garmin_id": garmin_id,
        "type": activity_type,
        "date": date_str,
        "duration_mins": duration_mins,
        "distance_km": distance_km,
        "avg_hr": val("avg_heart_rate"),
        "avg_pace": avg_pace,
        "calories": val("total_calories"),
    }
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_fit_parser.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/services/ backend/tests/test_fit_parser.py
git commit -m "feat: FIT file parser service"
```

---

### Task 5: Plan scheduler service

**Files:**
- Create: `backend/services/plan_scheduler.py`
- Create: `backend/tests/test_plan_scheduler.py`

**Interfaces:**
- Consumes: `TrainingPlan.json_structure` (JSON string), `plan_start_date: date`
- Produces: `schedule_plan(json_structure: str, start_date: date) -> list[dict]` where each dict has keys: `week`, `day`, `workout_type`, `target_distance_km`, `target_duration_mins`, `notes`, `date_scheduled`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_plan_scheduler.py
import json
from datetime import date
from services.plan_scheduler import schedule_plan

MINI_PLAN = json.dumps([
    {"week": 1, "days": [
        {"day": 1, "workout_type": "easy_run", "target_distance_km": 5.0, "notes": "Easy", "target_duration_mins": None},
        {"day": 7, "workout_type": "long_run",  "target_distance_km": 10.0, "notes": "Long", "target_duration_mins": None},
    ]},
    {"week": 2, "days": [
        {"day": 1, "workout_type": "easy_run", "target_distance_km": 6.0, "notes": "Easy", "target_duration_mins": None},
    ]},
])

def test_schedule_plan_monday_start():
    start = date(2026, 6, 23)  # a Monday
    rows = schedule_plan(MINI_PLAN, start)
    assert len(rows) == 3
    # Week 1 day 1 = Monday 2026-06-23
    assert rows[0]["date_scheduled"] == date(2026, 6, 23)
    # Week 1 day 7 = Sunday 2026-06-29
    assert rows[1]["date_scheduled"] == date(2026, 6, 29)
    # Week 2 day 1 = Monday 2026-06-30
    assert rows[2]["date_scheduled"] == date(2026, 6, 30)

def test_schedule_plan_preserves_fields():
    rows = schedule_plan(MINI_PLAN, date(2026, 6, 23))
    assert rows[0]["workout_type"] == "easy_run"
    assert rows[0]["target_distance_km"] == 5.0
    assert rows[0]["week"] == 1
    assert rows[0]["day"] == 1
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/test_plan_scheduler.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Create `backend/services/plan_scheduler.py`**

```python
import json
from datetime import date, timedelta

def schedule_plan(json_structure: str, start_date: date) -> list[dict]:
    weeks = json.loads(json_structure)
    rows = []
    for week_data in weeks:
        week_num = week_data["week"]
        week_offset = (week_num - 1) * 7
        for day_data in week_data["days"]:
            day_num = day_data["day"]  # 1=Mon, 7=Sun
            day_offset = day_num - 1
            scheduled = start_date + timedelta(days=week_offset + day_offset)
            rows.append({
                "week": week_num,
                "day": day_num,
                "workout_type": day_data.get("workout_type"),
                "target_distance_km": day_data.get("target_distance_km"),
                "target_duration_mins": day_data.get("target_duration_mins"),
                "notes": day_data.get("notes"),
                "date_scheduled": scheduled,
            })
    return rows
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_plan_scheduler.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/services/plan_scheduler.py backend/tests/test_plan_scheduler.py
git commit -m "feat: plan scheduler service"
```

---

### Task 6: Mobility recommendation engine

**Files:**
- Create: `backend/services/mobility_engine.py`
- Create: `backend/tests/test_mobility_engine.py`

**Interfaces:**
- Consumes: `Session`, `today: date`
- Produces: `recommend_routine(session: Session, today: date) -> str` returning a routine name from `mobility_routines.json`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_mobility_engine.py
from datetime import date, timedelta
from sqlmodel import Session
from models import Activity, PlanWorkout, MobilitySession, TrainingPlan, UserProfile
from services.mobility_engine import recommend_routine

def _add_activity(session, type_, distance_km, days_ago=0):
    d = date.today() - timedelta(days=days_ago)
    a = Activity(garmin_id=f"g_{type_}_{days_ago}", type=type_, date=d,
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
    session.add(UserProfile(id=1)); session.commit()
    result = recommend_routine(session, date.today())
    assert result == "Running Foundation"
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/test_mobility_engine.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Create `backend/services/mobility_engine.py`**

```python
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

    # Rule 4: rest day + no mobility this week
    week_start = today - timedelta(days=today.weekday())
    mobility_this_week = session.exec(
        select(Activity).where(
            Activity.date >= week_start,
            Activity.type == "run",
        )
    ).first()
    tomorrow_pw = session.exec(
        select(PlanWorkout).where(PlanWorkout.date_scheduled == today)
    ).first()
    is_rest_day = not tomorrow_pw or tomorrow_pw.workout_type == "rest"
    if is_rest_day and not mobility_this_week:
        return "Full Body Flexibility"

    # Rule 5: default
    return "Running Foundation"
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_mobility_engine.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/services/mobility_engine.py backend/tests/test_mobility_engine.py
git commit -m "feat: rules-based mobility recommendation engine"
```

---

### Task 7: Activities router

**Files:**
- Modify: `backend/routers/activities.py`
- Append to: `backend/tests/test_routes.py`

**Interfaces:**
- Produces: `GET /activities` → `list[Activity]`; `POST /activities/upload-fit` (multipart file) → `Activity`

- [ ] **Step 1: Write failing route tests — create `backend/tests/test_routes.py`**

```python
import io
from unittest.mock import patch
from datetime import date

def test_get_activities_empty(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert resp.json() == []

def test_upload_fit_file(client, tmp_path):
    fake_parsed = {
        "garmin_id": "20260601070000",
        "type": "run",
        "date": "2026-06-01",
        "duration_mins": 45.0,
        "distance_km": 8.0,
        "avg_hr": 148,
        "avg_pace": "5:37/km",
        "calories": 520,
    }
    fit_bytes = b"FIT_FAKE_BYTES"
    with patch("routers.activities.parse_fit_file", return_value=fake_parsed):
        resp = client.post(
            "/activities/upload-fit",
            files={"file": ("run.fit", io.BytesIO(fit_bytes), "application/octet-stream")},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["garmin_id"] == "20260601070000"
    assert body["type"] == "run"
    assert body["distance_km"] == 8.0

def test_upload_fit_duplicate(client):
    fake_parsed = {"garmin_id": "DUP1", "type": "run", "date": "2026-06-01",
                   "duration_mins": 30.0, "distance_km": 5.0,
                   "avg_hr": None, "avg_pace": None, "calories": None}
    fit_bytes = b"FAKE"
    with patch("routers.activities.parse_fit_file", return_value=fake_parsed):
        client.post("/activities/upload-fit", files={"file": ("a.fit", io.BytesIO(fit_bytes), "application/octet-stream")})
        resp = client.post("/activities/upload-fit", files={"file": ("b.fit", io.BytesIO(fit_bytes), "application/octet-stream")})
    assert resp.status_code == 409
```

- [ ] **Step 2: Verify failure**

```bash
pytest tests/test_routes.py -v
```

Expected: failures referencing empty router.

- [ ] **Step 3: Implement `backend/routers/activities.py`**

```python
import os, tempfile
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
    finally:
        os.unlink(tmp_path)

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
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_routes.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add backend/routers/activities.py backend/tests/test_routes.py
git commit -m "feat: activities router with FIT file upload"
```

---

### Task 8: Plans router

**Files:**
- Modify: `backend/routers/plans.py`
- Append tests to: `backend/tests/test_routes.py`

**Interfaces:**
- Produces: `GET /plans` → `list[TrainingPlan]`; `POST /plans/{id}/activate` → `UserProfile`; `GET /plans/workouts/today` → `PlanWorkout | null`; `PUT /plan-workouts/{id}` → `PlanWorkout`

- [ ] **Step 1: Add plan route tests to `backend/tests/test_routes.py`**

```python
# append to test_routes.py
from datetime import date as _date
import json

def _seed_plan(session):
    from models import TrainingPlan, UserProfile
    tp = TrainingPlan(name="Test 21k", distance="21k", duration_weeks=1,
                      json_structure=json.dumps([{"week":1,"days":[
                          {"day":1,"workout_type":"easy_run","target_distance_km":5.0,
                           "notes":"Easy","target_duration_mins":None}
                      ]}]))
    session.add(tp)
    session.add(UserProfile(id=1))
    session.commit()
    session.refresh(tp)
    return tp

def test_get_plans(client, session):
    _seed_plan(session)
    resp = client.get("/plans")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

def test_activate_plan(client, session):
    tp = _seed_plan(session)
    resp = client.post(f"/plans/{tp.id}/activate",
                       json={"start_date": str(_date.today())})
    assert resp.status_code == 200
    # plan workouts should be created
    from models import PlanWorkout
    from sqlmodel import select
    workouts = session.exec(select(PlanWorkout)).all()
    assert len(workouts) == 1

def test_update_plan_workout(client, session):
    from models import PlanWorkout, TrainingPlan, UserProfile
    tp = _seed_plan(session)
    pw = PlanWorkout(plan_id=tp.id, week=1, day=1, workout_type="easy_run",
                     target_distance_km=5.0, date_scheduled=_date.today())
    session.add(pw); session.commit(); session.refresh(pw)
    resp = client.put(f"/plans/workouts/{pw.id}", json={"target_distance_km": 7.0, "notes": "Pushed it"})
    assert resp.status_code == 200
    assert resp.json()["target_distance_km"] == 7.0
```

- [ ] **Step 2: Implement `backend/routers/plans.py`**

```python
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
    # clear existing workouts for this plan
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
    for field, value in body.dict(exclude_unset=True).items():
        setattr(pw, field, value)
    session.add(pw)
    session.commit()
    session.refresh(pw)
    return pw
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_routes.py -v
```

Expected: all passing.

- [ ] **Step 4: Commit**

```bash
git add backend/routers/plans.py
git commit -m "feat: plans router — activate plan, list workouts, update workout"
```

---

### Task 9: Mobility router

**Files:**
- Modify: `backend/routers/mobility.py`

**Interfaces:**
- Produces: `GET /mobility/routines` → `list[dict]`; `GET /mobility/recommendation` → `{routine_name, routine}`; `POST /mobility/sessions` → `MobilitySession`; `GET /mobility/sessions` → `list[MobilitySession]`

- [ ] **Step 1: Implement `backend/routers/mobility.py`**

```python
import json, os
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
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
```

- [ ] **Step 2: Test via Swagger**

```bash
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000/docs`. Try `GET /mobility/routines` — should return 8 routines. Try `GET /mobility/recommendation` — should return `"Running Foundation"` (no activities in DB yet). Stop server.

- [ ] **Step 3: Commit**

```bash
git add backend/routers/mobility.py
git commit -m "feat: mobility router — routines, recommendation, session logging"
```

---

### Task 10: Dashboard + Progress + Garmin routers

**Files:**
- Modify: `backend/routers/dashboard.py`
- Modify: `backend/routers/progress.py`
- Modify: `backend/routers/garmin.py`

**Interfaces:**
- Produces: `GET /dashboard` → summary dict; `GET /progress/charts` → chart data dict; `POST /garmin/sync` → stub response

- [ ] **Step 1: Implement `backend/routers/dashboard.py`**

```python
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from database import get_session
from models import Activity, PlanWorkout, MobilitySession, UserProfile
from services.mobility_engine import recommend_routine

router = APIRouter()

@router.get("")
def get_dashboard(session: Session = Depends(get_session)):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    today_workout = session.exec(
        select(PlanWorkout).where(PlanWorkout.date_scheduled == today)
    ).first()

    last_activity = session.exec(
        select(Activity).order_by(Activity.date.desc())
    ).first()

    week_activities = session.exec(
        select(Activity).where(Activity.date >= week_start)
    ).all()
    week_runs = [a for a in week_activities if a.type == "run"]
    week_crossfit = [a for a in week_activities if a.type == "crossfit"]
    total_km = sum(a.distance_km or 0 for a in week_runs)

    week_planned = session.exec(
        select(PlanWorkout).where(
            PlanWorkout.date_scheduled >= week_start,
            PlanWorkout.date_scheduled <= today,
            PlanWorkout.workout_type != "rest",
        )
    ).all()
    completed_count = sum(1 for w in week_planned if w.completed_activity_id is not None)

    routine_name = recommend_routine(session, today)

    return {
        "today_workout": today_workout,
        "last_activity": last_activity,
        "recommended_mobility": routine_name,
        "weekly_stats": {
            "km_this_week": round(total_km, 1),
            "crossfit_sessions": len(week_crossfit),
            "workouts_completed": completed_count,
            "workouts_planned": len(week_planned),
        },
    }
```

- [ ] **Step 2: Implement `backend/routers/progress.py`**

```python
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import Activity

router = APIRouter()

@router.get("/charts")
def get_charts(session: Session = Depends(get_session)):
    since = date.today() - timedelta(weeks=12)
    activities = session.exec(
        select(Activity).where(Activity.date >= since).order_by(Activity.date)
    ).all()

    # Pace trend: easy runs with pace data
    pace_trend = []
    for a in activities:
        if a.type == "run" and a.avg_pace:
            parts = a.avg_pace.replace("/km", "").split(":")
            if len(parts) == 2:
                pace_secs = int(parts[0]) * 60 + int(parts[1])
                pace_trend.append({"date": str(a.date), "pace_secs": pace_secs, "pace_label": a.avg_pace})

    # Weekly mileage
    weekly: dict[str, dict] = {}
    for a in activities:
        week_start = a.date - timedelta(days=a.date.weekday())
        key = str(week_start)
        if key not in weekly:
            weekly[key] = {"week": key, "run_km": 0.0, "crossfit_count": 0}
        if a.type == "run":
            weekly[key]["run_km"] += a.distance_km or 0
        elif a.type == "crossfit":
            weekly[key]["crossfit_count"] += 1
    weekly_mileage = sorted(weekly.values(), key=lambda x: x["week"])

    # HR trend
    hr_trend = [
        {"date": str(a.date), "avg_hr": a.avg_hr}
        for a in activities if a.avg_hr
    ]

    return {
        "pace_trend": pace_trend,
        "weekly_mileage": weekly_mileage,
        "hr_trend": hr_trend,
    }
```

- [ ] **Step 3: Implement `backend/routers/garmin.py`**

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/sync")
def sync_garmin():
    # Phase 2: implement with garminconnect library
    return {"status": "not_configured", "message": "Automated Garmin sync coming in Phase 2. Use FIT file upload on the Progress page."}
```

- [ ] **Step 4: Verify full API**

```bash
uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000/docs`. Check all 6 routers appear with their endpoints. Stop server.

- [ ] **Step 5: Commit**

```bash
git add backend/routers/dashboard.py backend/routers/progress.py backend/routers/garmin.py
git commit -m "feat: dashboard, progress charts, and garmin sync stub routers"
```

---

### Task 11: Frontend scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "running-app-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "axios": "^1.7.2",
    "recharts": "^2.12.7",
    "@fullcalendar/react": "^6.1.14",
    "@fullcalendar/daygrid": "^6.1.14",
    "@fullcalendar/interaction": "^6.1.14"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^5.2.12",
    "tailwindcss": "^3.4.4",
    "postcss": "^8.4.38",
    "autoprefixer": "^10.4.19"
  }
}
```

- [ ] **Step 2: Create `frontend/vite.config.js`**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        rewrite: path => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

- [ ] **Step 3: Create `frontend/tailwind.config.js`**

```js
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

- [ ] **Step 4: Create `frontend/postcss.config.js`**

```js
export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
}
```

- [ ] **Step 5: Create `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Running App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Create `frontend/src/main.jsx`**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 7: Create `frontend/src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 8: Install and verify**

```bash
cd frontend
npm install
npm run dev
```

Expected: Vite starts on `http://localhost:5173`. Browser shows blank white page (no App yet). Stop with Ctrl+C.

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: frontend scaffold — Vite, React, Tailwind"
```

---

### Task 12: API client + App shell

**Files:**
- Create: `frontend/src/api.js`
- Create: `frontend/src/App.jsx`

**Interfaces:**
- Produces: all API functions used by pages; `<App>` with nav and `<Routes>`

- [ ] **Step 1: Create `frontend/src/api.js`**

```js
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getDashboard = () => api.get('/dashboard').then(r => r.data)
export const getActivities = () => api.get('/activities').then(r => r.data)
export const uploadFit = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/activities/upload-fit', form).then(r => r.data)
}
export const getPlans = () => api.get('/plans').then(r => r.data)
export const activatePlan = (planId, startDate) =>
  api.post(`/plans/${planId}/activate`, { start_date: startDate }).then(r => r.data)
export const getWorkouts = () => api.get('/plans/workouts').then(r => r.data)
export const updateWorkout = (id, data) =>
  api.put(`/plans/workouts/${id}`, data).then(r => r.data)
export const getMobilityRoutines = (area) =>
  api.get('/mobility/routines', { params: area ? { area } : {} }).then(r => r.data)
export const getMobilityRecommendation = () =>
  api.get('/mobility/recommendation').then(r => r.data)
export const logMobilitySession = (data) =>
  api.post('/mobility/sessions', data).then(r => r.data)
export const getMobilitySessions = (days = 30) =>
  api.get('/mobility/sessions', { params: { days } }).then(r => r.data)
export const getProgressCharts = () => api.get('/progress/charts').then(r => r.data)
export const syncGarmin = () => api.post('/garmin/sync').then(r => r.data)
```

- [ ] **Step 2: Create `frontend/src/App.jsx`**

```jsx
import { BrowserRouter, NavLink, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Calendar from './pages/Calendar'
import TrainingPlan from './pages/TrainingPlan'
import Mobility from './pages/Mobility'
import Progress from './pages/Progress'

const NAV = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/calendar', label: 'Calendar' },
  { to: '/plan', label: 'Training Plan' },
  { to: '/mobility', label: 'Mobility' },
  { to: '/progress', label: 'Progress' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <nav className="bg-white border-b border-gray-200 px-6 py-3 flex gap-6 items-center">
          <span className="font-bold text-blue-600 text-lg mr-4">Running App</span>
          {NAV.map(n => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                `text-sm font-medium ${isActive ? 'text-blue-600' : 'text-gray-500 hover:text-gray-800'}`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <main className="flex-1 p-6 max-w-6xl mx-auto w-full">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/plan" element={<TrainingPlan />} />
            <Route path="/mobility" element={<Mobility />} />
            <Route path="/progress" element={<Progress />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
```

- [ ] **Step 3: Create empty page stubs so App.jsx doesn't crash**

Create each file with the same pattern:

`frontend/src/pages/Dashboard.jsx`:
```jsx
export default function Dashboard() { return <div className="text-gray-500">Dashboard loading...</div> }
```

Repeat for `Calendar.jsx`, `TrainingPlan.jsx`, `Mobility.jsx`, `Progress.jsx`.

- [ ] **Step 4: Verify nav renders**

```bash
# Terminal 1
cd backend && uvicorn main:app --reload --port 8000
# Terminal 2
cd frontend && npm run dev
```

Open `http://localhost:5173` — should see nav bar with 5 links and stub text for each page.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/
git commit -m "feat: API client, App shell with routing and nav"
```

---

### Task 13: Dashboard page

**Files:**
- Create: `frontend/src/components/WorkoutCard.jsx`
- Create: `frontend/src/components/MobilityCard.jsx`
- Create: `frontend/src/components/ActivitySummary.jsx`
- Create: `frontend/src/components/WeeklySnapshot.jsx`
- Modify: `frontend/src/pages/Dashboard.jsx`

- [ ] **Step 1: Create `frontend/src/components/WorkoutCard.jsx`**

```jsx
const TYPE_COLORS = {
  easy_run: 'bg-blue-100 text-blue-800',
  long_run: 'bg-purple-100 text-purple-800',
  tempo: 'bg-orange-100 text-orange-800',
  intervals: 'bg-red-100 text-red-800',
  cross_train: 'bg-green-100 text-green-800',
  rest: 'bg-gray-100 text-gray-600',
}

const TYPE_LABELS = {
  easy_run: 'Easy Run', long_run: 'Long Run', tempo: 'Tempo Run',
  intervals: 'Intervals', cross_train: 'Cross Train', rest: 'Rest Day',
}

export default function WorkoutCard({ workout }) {
  if (!workout) return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-sm text-gray-400">No workout scheduled for today.</p>
    </div>
  )
  const color = TYPE_COLORS[workout.workout_type] || 'bg-gray-100 text-gray-600'
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Today's Workout</p>
      <div className="flex items-center gap-3 mb-3">
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${color}`}>
          {TYPE_LABELS[workout.workout_type] || workout.workout_type}
        </span>
        {workout.target_distance_km && (
          <span className="text-gray-700 font-semibold">{workout.target_distance_km} km</span>
        )}
      </div>
      {workout.notes && <p className="text-sm text-gray-600">{workout.notes}</p>}
    </div>
  )
}
```

- [ ] **Step 2: Create `frontend/src/components/MobilityCard.jsx`**

```jsx
import { useState } from 'react'
import { logMobilitySession } from '../api'

export default function MobilityCard({ routineName, routine, onLogged }) {
  const [expanded, setExpanded] = useState(false)
  const [logging, setLogging] = useState(false)
  const [done, setDone] = useState(false)

  const markDone = async () => {
    setLogging(true)
    try {
      await logMobilitySession({ routine_name: routineName, duration_mins: routine?.duration_mins || 10, recommended: true })
      setDone(true)
      onLogged?.()
    } finally {
      setLogging(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Mobility Today</p>
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="font-semibold text-gray-800">{routineName}</p>
          {routine && <p className="text-sm text-gray-500">{routine.duration_mins} min · {routine.areas.join(', ')}</p>}
        </div>
        {done ? (
          <span className="text-green-600 font-medium text-sm">Done ✓</span>
        ) : (
          <button onClick={markDone} disabled={logging}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
            {logging ? '...' : 'Mark Done'}
          </button>
        )}
      </div>
      {routine?.exercises && (
        <button onClick={() => setExpanded(!expanded)}
          className="text-sm text-blue-600 hover:underline">
          {expanded ? 'Hide exercises' : 'Show exercises'}
        </button>
      )}
      {expanded && routine?.exercises && (
        <ul className="mt-3 space-y-1">
          {routine.exercises.map((ex, i) => (
            <li key={i} className="text-sm text-gray-600 flex gap-2">
              <span className="text-gray-400">{Math.floor(ex.duration_secs / 60)}:{String(ex.duration_secs % 60).padStart(2,'0')}</span>
              <span>{ex.name}</span>
              {ex.cue && <span className="text-gray-400">— {ex.cue}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Create `frontend/src/components/ActivitySummary.jsx`**

```jsx
export default function ActivitySummary({ activity }) {
  if (!activity) return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Last Activity</p>
      <p className="text-sm text-gray-400">No activities synced yet. Upload a FIT file on the Progress page.</p>
    </div>
  )
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Last Activity</p>
      <p className="font-semibold text-gray-800 capitalize mb-2">{activity.type} — {activity.date}</p>
      <div className="flex gap-4 text-sm text-gray-600">
        {activity.distance_km && <span>{activity.distance_km} km</span>}
        {activity.avg_pace && <span>{activity.avg_pace}</span>}
        {activity.avg_hr && <span>{activity.avg_hr} bpm</span>}
        {activity.duration_mins && <span>{Math.round(activity.duration_mins)} min</span>}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create `frontend/src/components/WeeklySnapshot.jsx`**

```jsx
export default function WeeklySnapshot({ stats }) {
  if (!stats) return null
  const pct = stats.workouts_planned > 0
    ? Math.round((stats.workouts_completed / stats.workouts_planned) * 100)
    : 0
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">This Week</p>
      <div className="flex gap-6">
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-800">{stats.km_this_week}</p>
          <p className="text-xs text-gray-500">km run</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-800">{stats.crossfit_sessions}</p>
          <p className="text-xs text-gray-500">CrossFit</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-gray-800">{stats.workouts_completed}/{stats.workouts_planned}</p>
          <p className="text-xs text-gray-500">workouts done</p>
        </div>
      </div>
      <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Implement `frontend/src/pages/Dashboard.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { getDashboard, getMobilityRecommendation } from '../api'
import WorkoutCard from '../components/WorkoutCard'
import MobilityCard from '../components/MobilityCard'
import ActivitySummary from '../components/ActivitySummary'
import WeeklySnapshot from '../components/WeeklySnapshot'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [mobility, setMobility] = useState(null)
  const [error, setError] = useState(null)

  const load = async () => {
    try {
      const [dash, mob] = await Promise.all([getDashboard(), getMobilityRecommendation()])
      setData(dash)
      setMobility(mob)
    } catch (e) {
      setError('Could not load dashboard. Is the backend running?')
    }
  }

  useEffect(() => { load() }, [])

  if (error) return <p className="text-red-500">{error}</p>
  if (!data) return <p className="text-gray-400">Loading...</p>

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-800">
        {new Date().toLocaleDateString('en-ZA', { weekday: 'long', day: 'numeric', month: 'long' })}
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <WorkoutCard workout={data.today_workout} />
        {mobility && (
          <MobilityCard
            routineName={mobility.routine_name}
            routine={mobility.routine}
            onLogged={load}
          />
        )}
      </div>
      <ActivitySummary activity={data.last_activity} />
      <WeeklySnapshot stats={data.weekly_stats} />
    </div>
  )
}
```

- [ ] **Step 6: Verify in browser**

With both servers running, open `http://localhost:5173/dashboard`. Should see all four cards rendering (empty states are fine before any data is loaded).

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/ frontend/src/pages/Dashboard.jsx
git commit -m "feat: Dashboard page with workout, mobility, activity, and weekly stats cards"
```

---

### Task 14: Calendar page

**Files:**
- Modify: `frontend/src/pages/Calendar.jsx`

- [ ] **Step 1: Implement `frontend/src/pages/Calendar.jsx`**

```jsx
import { useEffect, useState } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import interactionPlugin from '@fullcalendar/interaction'
import { getWorkouts, updateWorkout } from '../api'

const TYPE_COLORS = {
  easy_run: '#3b82f6', long_run: '#8b5cf6', tempo: '#f97316',
  intervals: '#ef4444', cross_train: '#10b981', rest: '#d1d5db',
}

const TYPE_LABELS = {
  easy_run: 'Easy', long_run: 'Long Run', tempo: 'Tempo',
  intervals: 'Intervals', cross_train: 'Cross', rest: 'Rest',
}

export default function Calendar() {
  const [workouts, setWorkouts] = useState([])
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    getWorkouts().then(setWorkouts).catch(() => {})
  }, [])

  const events = workouts.map(w => ({
    id: String(w.id),
    title: `${TYPE_LABELS[w.workout_type] || w.workout_type}${w.target_distance_km ? ` ${w.target_distance_km}km` : ''}`,
    date: w.date_adjusted || w.date_scheduled,
    backgroundColor: TYPE_COLORS[w.workout_type] || '#9ca3af',
    borderColor: w.completed_activity_id ? '#15803d' : 'transparent',
    textColor: w.workout_type === 'rest' ? '#6b7280' : '#fff',
    extendedProps: { workout: w },
  }))

  const handleEventDrop = async (info) => {
    const w = info.event.extendedProps.workout
    const newDate = info.event.startStr
    await updateWorkout(w.id, { date_adjusted: newDate })
    setWorkouts(prev => prev.map(pw => pw.id === w.id ? { ...pw, date_adjusted: newDate } : pw))
  }

  const handleEventClick = (info) => {
    setSelected(info.event.extendedProps.workout)
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <FullCalendar
        plugins={[dayGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        events={events}
        editable={true}
        eventDrop={handleEventDrop}
        eventClick={handleEventClick}
        height="auto"
      />
      {selected && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex justify-between items-start">
            <div>
              <p className="font-semibold">{TYPE_LABELS[selected.workout_type]}</p>
              {selected.target_distance_km && <p className="text-sm text-gray-600">{selected.target_distance_km} km</p>}
              {selected.notes && <p className="text-sm text-gray-500 mt-1">{selected.notes}</p>}
              {selected.completed_activity_id && <p className="text-sm text-green-600 mt-1">Completed ✓</p>}
            </div>
            <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-600">✕</button>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Verify in browser**

Open `http://localhost:5173/calendar`. Calendar grid renders. (Empty until plan is activated.)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Calendar.jsx
git commit -m "feat: Calendar page with FullCalendar and drag-to-reschedule"
```

---

### Task 15: Training Plan page

**Files:**
- Create: `frontend/src/components/WorkoutEditor.jsx`
- Modify: `frontend/src/pages/TrainingPlan.jsx`

- [ ] **Step 1: Create `frontend/src/components/WorkoutEditor.jsx`**

```jsx
import { useState } from 'react'
import { updateWorkout } from '../api'

const TYPES = ['easy_run','long_run','tempo','intervals','cross_train','rest']

export default function WorkoutEditor({ workout, onSaved }) {
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({
    workout_type: workout.workout_type,
    target_distance_km: workout.target_distance_km || '',
    notes: workout.notes || '',
  })
  const [saving, setSaving] = useState(false)

  const save = async () => {
    setSaving(true)
    try {
      const updated = await updateWorkout(workout.id, {
        workout_type: form.workout_type,
        target_distance_km: form.target_distance_km ? Number(form.target_distance_km) : null,
        notes: form.notes || null,
      })
      onSaved(updated)
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  if (!editing) return (
    <button onClick={() => setEditing(true)} className="text-xs text-blue-500 hover:underline">edit</button>
  )

  return (
    <div className="flex flex-col gap-2 mt-1">
      <select value={form.workout_type} onChange={e => setForm(f => ({...f, workout_type: e.target.value}))}
        className="text-xs border rounded px-1 py-0.5">
        {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
      </select>
      <input type="number" placeholder="km" value={form.target_distance_km}
        onChange={e => setForm(f => ({...f, target_distance_km: e.target.value}))}
        className="text-xs border rounded px-1 py-0.5 w-20" />
      <input type="text" placeholder="notes" value={form.notes}
        onChange={e => setForm(f => ({...f, notes: e.target.value}))}
        className="text-xs border rounded px-1 py-0.5" />
      <div className="flex gap-2">
        <button onClick={save} disabled={saving}
          className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded disabled:opacity-50">
          {saving ? '...' : 'Save'}
        </button>
        <button onClick={() => setEditing(false)} className="text-xs text-gray-400 hover:text-gray-600">Cancel</button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Implement `frontend/src/pages/TrainingPlan.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { getPlans, activatePlan, getWorkouts } from '../api'
import WorkoutEditor from '../components/WorkoutEditor'

const DAY_NAMES = ['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const TYPE_COLORS = {
  easy_run: 'bg-blue-100 text-blue-700', long_run: 'bg-purple-100 text-purple-700',
  tempo: 'bg-orange-100 text-orange-700', intervals: 'bg-red-100 text-red-700',
  cross_train: 'bg-green-100 text-green-700', rest: 'bg-gray-100 text-gray-500',
}

export default function TrainingPlan() {
  const [plans, setPlans] = useState([])
  const [workouts, setWorkouts] = useState([])
  const [selectedPlanId, setSelectedPlanId] = useState('')
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0])
  const [activating, setActivating] = useState(false)

  useEffect(() => {
    getPlans().then(setPlans)
    getWorkouts().then(setWorkouts)
  }, [])

  const activate = async () => {
    if (!selectedPlanId) return
    if (!window.confirm('Activating a new plan will reset your current schedule. Continue?')) return
    setActivating(true)
    try {
      await activatePlan(Number(selectedPlanId), startDate)
      const updated = await getWorkouts()
      setWorkouts(updated)
    } finally {
      setActivating(false)
    }
  }

  const grouped = workouts.reduce((acc, w) => {
    if (!acc[w.week]) acc[w.week] = []
    acc[w.week].push(w)
    return acc
  }, {})

  const weeks = Object.keys(grouped).sort((a, b) => Number(a) - Number(b))
  const currentWeek = weeks.find(wk =>
    grouped[wk].some(w => w.date_scheduled && new Date(w.date_scheduled) >= new Date(new Date().toDateString()))
  ) || weeks[0]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Plan</label>
          <select value={selectedPlanId} onChange={e => setSelectedPlanId(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm">
            <option value="">Select a plan...</option>
            {plans.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Start Date (Monday)</label>
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)}
            className="border rounded px-3 py-1.5 text-sm" />
        </div>
        <button onClick={activate} disabled={!selectedPlanId || activating}
          className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {activating ? 'Activating...' : 'Activate Plan'}
        </button>
      </div>

      {weeks.map(wk => (
        <div key={wk} className={`bg-white rounded-xl border p-5 ${wk === currentWeek ? 'border-blue-400' : 'border-gray-200'}`}>
          <p className="font-semibold text-gray-700 mb-3">
            Week {wk} {wk === currentWeek && <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Current</span>}
          </p>
          <div className="grid grid-cols-7 gap-2">
            {grouped[wk].sort((a,b) => a.day - b.day).map(w => (
              <div key={w.id} className={`rounded-lg p-2 text-xs ${TYPE_COLORS[w.workout_type] || 'bg-gray-100 text-gray-600'}`}>
                <p className="font-semibold">{DAY_NAMES[w.day]}</p>
                <p>{w.workout_type.replace('_', ' ')}</p>
                {w.target_distance_km && <p>{w.target_distance_km}km</p>}
                <WorkoutEditor
                  workout={w}
                  onSaved={updated => setWorkouts(prev => prev.map(pw => pw.id === updated.id ? updated : pw))}
                />
              </div>
            ))}
          </div>
        </div>
      ))}
      {weeks.length === 0 && <p className="text-gray-400 text-sm">No plan activated yet. Select a plan above and click Activate.</p>}
    </div>
  )
}
```

- [ ] **Step 3: Verify in browser**

Open `http://localhost:5173/plan`. Select "Hal Higdon 21k Novice", pick a start date, click Activate. Should see 12 weeks of colour-coded workout grids appear.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/TrainingPlan.jsx frontend/src/components/WorkoutEditor.jsx
git commit -m "feat: Training Plan page with week grid and inline workout editing"
```

---

### Task 16: Mobility page

**Files:**
- Create: `frontend/src/components/RoutineCard.jsx`
- Modify: `frontend/src/pages/Mobility.jsx`

- [ ] **Step 1: Create `frontend/src/components/RoutineCard.jsx`**

```jsx
import { useState } from 'react'
import { logMobilitySession } from '../api'

export default function RoutineCard({ routine, onLogged }) {
  const [expanded, setExpanded] = useState(false)
  const [logging, setLogging] = useState(false)

  const log = async () => {
    setLogging(true)
    try {
      await logMobilitySession({ routine_name: routine.name, duration_mins: routine.duration_mins })
      onLogged?.()
    } finally {
      setLogging(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex justify-between items-start mb-2">
        <div>
          <p className="font-semibold text-gray-800 text-sm">{routine.name}</p>
          <p className="text-xs text-gray-500">{routine.duration_mins} min · {routine.areas.join(', ')}</p>
        </div>
        <button onClick={log} disabled={logging}
          className="text-xs px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {logging ? '...' : 'Log'}
        </button>
      </div>
      <button onClick={() => setExpanded(!expanded)} className="text-xs text-blue-500 hover:underline">
        {expanded ? 'Hide' : 'Show exercises'}
      </button>
      {expanded && (
        <ul className="mt-2 space-y-1">
          {routine.exercises.map((ex, i) => (
            <li key={i} className="text-xs text-gray-600 flex gap-2">
              <span className="text-gray-400 shrink-0">
                {Math.floor(ex.duration_secs/60)}:{String(ex.duration_secs%60).padStart(2,'0')}
              </span>
              <span>{ex.name}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

- [ ] **Step 2: Implement `frontend/src/pages/Mobility.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { getMobilityRoutines, getMobilityRecommendation, getMobilitySessions } from '../api'
import MobilityCard from '../components/MobilityCard'
import RoutineCard from '../components/RoutineCard'

const AREAS = ['all', 'hips', 'calves', 'ankles', 'full_body', 'thoracic', 'glutes', 'shoulders']

export default function Mobility() {
  const [recommendation, setRecommendation] = useState(null)
  const [routines, setRoutines] = useState([])
  const [sessions, setSessions] = useState([])
  const [areaFilter, setAreaFilter] = useState('all')

  const loadAll = async () => {
    const [rec, rts, sess] = await Promise.all([
      getMobilityRecommendation(),
      getMobilityRoutines(),
      getMobilitySessions(30),
    ])
    setRecommendation(rec)
    setRoutines(rts)
    setSessions(sess)
  }

  useEffect(() => { loadAll() }, [])

  const filteredRoutines = areaFilter === 'all'
    ? routines
    : routines.filter(r => r.areas.includes(areaFilter))

  return (
    <div className="space-y-6">
      {recommendation && (
        <div>
          <h2 className="text-lg font-bold text-gray-800 mb-3">Recommended Today</h2>
          <MobilityCard
            routineName={recommendation.routine_name}
            routine={recommendation.routine}
            onLogged={loadAll}
          />
        </div>
      )}

      <div>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-lg font-bold text-gray-800">Routine Library</h2>
          <select value={areaFilter} onChange={e => setAreaFilter(e.target.value)}
            className="text-sm border rounded px-2 py-1">
            {AREAS.map(a => <option key={a} value={a}>{a === 'all' ? 'All areas' : a}</option>)}
          </select>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredRoutines.map(r => (
            <RoutineCard key={r.name} routine={r} onLogged={loadAll} />
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-bold text-gray-800 mb-3">History (last 30 days)</h2>
        {sessions.length === 0
          ? <p className="text-sm text-gray-400">No sessions logged yet.</p>
          : (
            <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
              {sessions.map(s => (
                <div key={s.id} className="flex justify-between items-center px-4 py-3 text-sm">
                  <div>
                    <p className="font-medium text-gray-800">{s.routine_name}</p>
                    <p className="text-gray-500 text-xs">{s.date}</p>
                  </div>
                  <p className="text-gray-600">{s.duration_mins} min</p>
                </div>
              ))}
            </div>
          )
        }
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Verify in browser**

Open `http://localhost:5173/mobility`. Should see recommended routine, full library of 8 routines, filter dropdown, and empty history.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Mobility.jsx frontend/src/components/RoutineCard.jsx
git commit -m "feat: Mobility page with recommendation, library, and session history"
```

---

### Task 17: Progress page

**Files:**
- Create: `frontend/src/components/PaceChart.jsx`
- Create: `frontend/src/components/MileageChart.jsx`
- Create: `frontend/src/components/FitUpload.jsx`
- Modify: `frontend/src/pages/Progress.jsx`

- [ ] **Step 1: Create `frontend/src/components/PaceChart.jsx`**

```jsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

function paceLabel(secs) {
  const m = Math.floor(secs / 60), s = secs % 60
  return `${m}:${String(s).padStart(2,'0')}/km`
}

export default function PaceChart({ data }) {
  if (!data?.length) return <p className="text-sm text-gray-400">No pace data yet. Import some runs.</p>
  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={d => d.slice(5)} />
        <YAxis reversed domain={['auto','auto']} tick={{ fontSize: 11 }}
          tickFormatter={paceLabel} />
        <Tooltip formatter={(v) => paceLabel(v)} labelFormatter={l => `Date: ${l}`} />
        <Line type="monotone" dataKey="pace_secs" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 2: Create `frontend/src/components/MileageChart.jsx`**

```jsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts'

export default function MileageChart({ data }) {
  if (!data?.length) return <p className="text-sm text-gray-400">No mileage data yet.</p>
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="week" tick={{ fontSize: 11 }} tickFormatter={d => d.slice(5)} />
        <YAxis tick={{ fontSize: 11 }} unit="km" />
        <Tooltip formatter={(v, n) => n === 'run_km' ? [`${v.toFixed(1)} km`, 'Running'] : [v, 'CrossFit sessions']} />
        <Bar dataKey="run_km" fill="#3b82f6" radius={[3,3,0,0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 3: Create `frontend/src/components/FitUpload.jsx`**

```jsx
import { useRef, useState } from 'react'
import { uploadFit } from '../api'

export default function FitUpload({ onUploaded }) {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState(null)
  const inputRef = useRef()

  const handleFiles = async (files) => {
    for (const file of files) {
      if (!file.name.endsWith('.fit')) { setMessage('Only .fit files accepted'); continue }
      setUploading(true)
      setMessage(null)
      try {
        await uploadFit(file)
        setMessage(`Imported: ${file.name}`)
        onUploaded?.()
      } catch (e) {
        setMessage(e.response?.data?.detail === 'Activity already imported'
          ? `${file.name}: already imported`
          : `${file.name}: upload failed`)
      } finally {
        setUploading(false)
      }
    }
  }

  const onDrop = (e) => { e.preventDefault(); handleFiles(e.dataTransfer.files) }
  const onDragOver = (e) => e.preventDefault()

  return (
    <div>
      <div
        onDrop={onDrop} onDragOver={onDragOver}
        onClick={() => inputRef.current.click()}
        className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors"
      >
        <p className="text-gray-500 text-sm">{uploading ? 'Importing...' : 'Drop .fit files here, or click to select'}</p>
        <input ref={inputRef} type="file" accept=".fit" multiple className="hidden"
          onChange={e => handleFiles(e.target.files)} />
      </div>
      {message && <p className="mt-2 text-sm text-gray-600">{message}</p>}
    </div>
  )
}
```

- [ ] **Step 4: Implement `frontend/src/pages/Progress.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { getProgressCharts, syncGarmin } from '../api'
import PaceChart from '../components/PaceChart'
import MileageChart from '../components/MileageChart'
import FitUpload from '../components/FitUpload'

export default function Progress() {
  const [charts, setCharts] = useState(null)
  const [syncing, setSyncing] = useState(false)
  const [syncMsg, setSyncMsg] = useState(null)

  const loadCharts = () => getProgressCharts().then(setCharts)
  useEffect(() => { loadCharts() }, [])

  const handleSync = async () => {
    setSyncing(true)
    try {
      const res = await syncGarmin()
      setSyncMsg(res.message)
    } catch {
      setSyncMsg('Sync failed.')
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-bold text-gray-800 mb-4">Sync Garmin Data</h2>
        <FitUpload onUploaded={loadCharts} />
        <div className="mt-4 flex items-center gap-3">
          <button onClick={handleSync} disabled={syncing}
            className="px-4 py-2 bg-gray-800 text-white text-sm rounded-lg hover:bg-gray-700 disabled:opacity-50">
            {syncing ? 'Syncing...' : 'Sync from Garmin Connect'}
          </button>
          {syncMsg && <p className="text-sm text-gray-500">{syncMsg}</p>}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-bold text-gray-800 mb-4">Easy Run Pace Trend</h2>
        <PaceChart data={charts?.pace_trend} />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-bold text-gray-800 mb-4">Weekly Mileage</h2>
        <MileageChart data={charts?.weekly_mileage} />
      </div>

      {charts?.hr_trend?.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="font-bold text-gray-800 mb-3">Heart Rate Trend</h2>
          <p className="text-sm text-gray-500">
            Latest avg HR: {charts.hr_trend[charts.hr_trend.length - 1]?.avg_hr} bpm
          </p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 5: Verify in browser**

Open `http://localhost:5173/progress`. Should see FIT upload zone, Garmin sync button (returns Phase 2 message), and empty chart states. Drop a real `.fit` file in — activity should import and pace/mileage charts populate.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/Progress.jsx frontend/src/components/PaceChart.jsx frontend/src/components/MileageChart.jsx frontend/src/components/FitUpload.jsx
git commit -m "feat: Progress page with pace/mileage charts and FIT file upload"
```

---

### Task 18: Final integration check

- [ ] **Step 1: Run full backend test suite**

```bash
cd backend
pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 2: End-to-end smoke test**

With both servers running:
1. Go to `http://localhost:5173/plan` — activate "Hal Higdon 21k Novice" starting next Monday
2. Go to `/calendar` — verify workouts appear colour-coded
3. Go to `/dashboard` — verify today's workout card and mobility recommendation appear
4. Go to `/progress` — drop in a `.fit` export from Garmin Connect; verify activity imports
5. Go to `/dashboard` — verify "Last Activity" now shows the imported run
6. Go to `/mobility` — click "Mark Done" on the recommendation; verify it logs in History

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: running app complete — all 5 pages implemented and verified"
```

