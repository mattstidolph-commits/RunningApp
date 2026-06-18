# Running App — Design Spec
**Date:** 2026-06-18
**Status:** Approved

---

## Overview

A locally-run personal training dashboard for a runner targeting 21k and 42k distances, with ambitions to progress further. The user also does CrossFit and daily walks, so the app must account for total training load across all activities — not just running mileage. The core problem it solves: having a structured, adaptive plan that the user can see in one place, with guided mobility work to support running performance and reduce injury risk.

**Success in 6 months:** Consistently following a structured plan, hitting 21k/42k targets without injury, visibly improving pace and recovery, and feeling better running.

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Browser (React + Vite)        │
│  Dashboard │ Calendar │ Plans │ Mobility│
└────────────────────┬────────────────────┘
                     │ HTTP / REST
┌────────────────────▼────────────────────┐
│         Python FastAPI Backend          │
│  Routes │ Training Logic │ Sync Engine  │
└────────────────────┬────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────┐        ┌────────▼────────┐
│  SQLite DB   │        │  Garmin Connect  │
│ (local file) │        │  (garminconnect  │
│              │        │   Python lib)    │
└──────────────┘        └─────────────────┘
```

**Technology stack:**
- **Backend:** Python 3.11+, FastAPI, SQLite (via SQLModel — built on SQLAlchemy, pairs natively with FastAPI's Pydantic models), `garminconnect` library, `fitparse` for FIT file parsing
- **Frontend:** React 18, Vite, Recharts (charts), FullCalendar (training calendar), Tailwind CSS
- **Local setup:** Two processes — `uvicorn` for the backend (port 8000), `vite` for the frontend (port 5173)
- **No cloud dependencies.** Everything runs on the user's machine. No subscriptions.

---

## Data Model

### `activities`
Synced from Garmin. One row per recorded activity.

| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER PK | |
| garmin_id | TEXT UNIQUE | Prevents duplicate imports |
| type | TEXT | `run`, `crossfit`, `walk`, `other` |
| date | DATE | |
| duration_mins | REAL | |
| distance_km | REAL | Null for CrossFit |
| avg_hr | INTEGER | Beats per minute |
| avg_pace | TEXT | e.g. `5:30/km` — runs only |
| calories | INTEGER | |
| raw_fit_path | TEXT | Path to local .fit file if imported |

### `training_plans`
Pre-built plan templates. Loaded from bundled JSON files.

| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER PK | |
| name | TEXT | e.g. "Hal Higdon 21k Novice" |
| distance | TEXT | `21k` or `42k` |
| duration_weeks | INTEGER | |
| json_structure | TEXT | JSON array of weeks → days → workouts |

### `plan_workouts`
The user's active plan, one row per scheduled workout day.

| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER PK | |
| plan_id | INTEGER FK | References `training_plans` |
| week | INTEGER | Week number in the plan |
| day | INTEGER | Day of week (1=Mon, 7=Sun) |
| workout_type | TEXT | `easy_run`, `long_run`, `tempo`, `intervals`, `rest`, `cross_train` |
| target_distance_km | REAL | Nullable (rest days) |
| target_duration_mins | INTEGER | Nullable |
| notes | TEXT | Coach notes for this workout |
| completed_activity_id | INTEGER FK | Links to `activities` when done |
| date_scheduled | DATE | Computed from plan start date |
| date_adjusted | DATE | Set when user manually reschedules |

### `mobility_sessions`
Logged mobility work, whether recommended or user-chosen.

| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER PK | |
| date | DATE | |
| routine_name | TEXT | e.g. "Hip Flexor Recovery" |
| duration_mins | INTEGER | |
| notes | TEXT | Optional |
| completed | BOOLEAN | |
| recommended | BOOLEAN | True if surfaced by the recommendation engine |

### `user_profile`
Single-row config table.

| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER PK | Always 1 |
| name | TEXT | |
| target_race | TEXT | e.g. "Cape Town Marathon" |
| target_race_date | DATE | |
| garmin_email | TEXT | For automated sync |
| weekly_crossfit_days | INTEGER | Used in load calculation |
| current_plan_id | INTEGER FK | Active training plan |
| plan_start_date | DATE | When the active plan began |

---

## Mobility Recommendation Engine

Rules-based logic that runs on page load and surfaces one routine per day on the Dashboard.

**Rules (evaluated in priority order):**

1. **Day after long run** (activity type=run AND distance ≥ 10km for 21k plans, ≥ 15km for 42k plans) → "Post Long Run Recovery" (hips, calves, hamstrings — 15 min)
2. **Day before long run** (tomorrow's plan_workout is long_run) → "Pre Long Run Activation" (glutes, ankles, dynamic warm-up — 10 min)
3. **CrossFit day** (today's activity type=crossfit) → "Upper Body & Thoracic Mobility" (shoulders, thoracic spine — 12 min)
4. **Rest day with no prior mobility this week** → "Full Body Flexibility" (30 min)
5. **Default / easy run day** → "Running Foundation" (calves, hip flexors, ankles — 10 min)

**Library:** 8–10 pre-built routines bundled as JSON, each with a name, target body areas, duration, and ordered list of exercises (name + duration in seconds + optional cue).

The user can always override the recommendation by choosing a different routine from the library.

---

## Features & Pages

### 1. Dashboard
**Purpose:** Open the app, know exactly what to do today.

- Today's planned workout card (type, target distance/duration, coach notes)
- Today's recommended mobility routine card with one-tap "Mark Done"
- Last synced Garmin activity summary (type, distance, pace, HR)
- Weekly snapshot bar: X of Y workouts completed, total km this week, CrossFit sessions
- Quick actions: Sync Garmin, Upload FIT file

### 2. Calendar
**Purpose:** See the full training picture across a month.

- Monthly calendar grid (FullCalendar)
- Each day shows planned workout type and completion status
- Colour coding: completed (green), missed (red), upcoming (grey), rest day (blue)
- Click a day → detail panel (planned vs actual, mobility logged)
- Drag a planned workout to reschedule it (updates `date_adjusted`)

### 3. Training Plan
**Purpose:** Manage the active plan and make adjustments.

- Week-by-week table of the active plan
- Current week highlighted, progress bar (weeks completed / total)
- Race countdown (days to target race date)
- Edit any workout: change type, distance, duration, or notes inline
- Switch plan: dropdown to select a different pre-built plan (prompts to confirm — resets schedule)
- Pre-built plans included at launch: Hal Higdon 21k Novice, Hal Higdon 42k Novice, Hal Higdon 42k Intermediate

### 4. Mobility
**Purpose:** Follow guided routines and track consistency.

- Today's recommended routine (expandable: exercise list with durations)
- Full library grid (cards per routine, filterable by: Hips, Calves, Ankles, Full Body, Upper Body)
- Log a session: pick routine → set duration → add notes → save
- 30-day history list (date, routine, duration)

### 5. Progress
**Purpose:** See fitness improving over time.

- Easy run pace trend (line chart, last 12 weeks)
- Weekly mileage bar chart (last 12 weeks, with CrossFit days marked)
- Training load chart (combined: running km + CrossFit session count as weighted contribution)
- Resting HR trend (if available from Garmin data)
- Garmin sync panel:
  - Manual: drag-and-drop FIT file upload
  - Automated: "Sync from Garmin Connect" button (uses stored credentials, fetches last 30 activities)

---

## Garmin Integration

**Phase 1 (launch):** Manual FIT file import. User exports `.fit` files from Garmin Connect website and uploads via the Progress page drag-and-drop. Backend parses with `fitparse`, extracts fields, stores in `activities`.

**Phase 2 (follow-up):** Automated sync using the `garminconnect` Python library. Credentials stored locally (encrypted with `keyring`). One-click sync fetches recent activities from Garmin Connect. Replaces manual upload for day-to-day use; manual import remains as fallback.

---

## Local Setup

```
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

Database file (`running.db`) created automatically on first run in the `backend/` directory.

---

## Out of Scope (Phase 1)

- AI/ML-based plan adaptation (rule-based recommendations only)
- Mobile app or PWA
- Multi-user support
- Integration with other platforms (Strava, Apple Health)
- Video guides for mobility exercises
- Automated plan adjustment based on missed workouts (manual adjustment only)
