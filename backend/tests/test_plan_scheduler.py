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
    assert rows[0]["date_scheduled"] == date(2026, 6, 23)  # Week 1 Mon
    assert rows[1]["date_scheduled"] == date(2026, 6, 29)  # Week 1 Sun
    assert rows[2]["date_scheduled"] == date(2026, 6, 30)  # Week 2 Mon

def test_schedule_plan_preserves_fields():
    rows = schedule_plan(MINI_PLAN, date(2026, 6, 23))
    assert rows[0]["workout_type"] == "easy_run"
    assert rows[0]["target_distance_km"] == 5.0
    assert rows[0]["week"] == 1
    assert rows[0]["day"] == 1
