"""Run once: python seed_data.py"""
import json
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
            make_week(4,  [6,8,6],   11),
            make_week(5,  [6,8,6],   14),
            make_week(6,  [8,8,8],   16),
            make_week(7,  [8,8,8],   14),
            make_week(8,  [8,10,8],  18),
            make_week(9,  [8,10,8],  16),
            make_week(10, [10,10,10],19),
            make_week(11, [8,6,5],   11),
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
            make_week(4,  [5,5,5],   11),
            make_week(5,  [6,6,6],   16),
            make_week(6,  [6,6,6],   18),
            make_week(7,  [6,6,6],   16),
            make_week(8,  [6,6,6],   21),
            make_week(9,  [8,8,8],   18),
            make_week(10, [8,8,8],   26),
            make_week(11, [8,8,8],   24),
            make_week(12, [10,10,10],29),
            make_week(13, [8,8,8],   24),
            make_week(14, [10,10,10],32),
            make_week(15, [8,8,8],   29),
            make_week(16, [10,10,10],32),
            make_week(17, [8,6,5],   19),
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
            make_week(4,  [6,6,6],   13, has_tempo=True, tempo_km=6),
            make_week(5,  [8,8,8],   18, has_tempo=True, tempo_km=8),
            make_week(6,  [8,8,8],   21, has_tempo=True, tempo_km=8),
            make_week(7,  [8,8,8],   18, has_tempo=True, tempo_km=8),
            make_week(8,  [10,10,10],24, has_tempo=True, tempo_km=10),
            make_week(9,  [8,8,8],   21, has_tempo=True, tempo_km=8),
            make_week(10, [10,10,10],27, has_tempo=True, tempo_km=10),
            make_week(11, [10,10,10],24, has_tempo=True, tempo_km=10),
            make_week(12, [10,10,10],32, has_tempo=True, tempo_km=10),
            make_week(13, [10,10,10],27, has_tempo=True, tempo_km=10),
            make_week(14, [10,10,10],32, has_tempo=True, tempo_km=10),
            make_week(15, [10,10,10],29, has_tempo=True, tempo_km=10),
            make_week(16, [10,10,10],32, has_tempo=True, tempo_km=10),
            make_week(17, [8,6,5],   19),
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
         {"name": "Doorway Chest Stretch", "duration_secs": 45, "cue": "Arms at 90 degrees, lean gently forward"},
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
         {"name": "Doorway Chest Stretch", "duration_secs": 45, "cue": "Arms at 90 degrees"},
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
                select(TrainingPlan).where(TrainingPlan.name == p["name"])
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
