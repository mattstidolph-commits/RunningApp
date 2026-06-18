import pytest
from unittest.mock import patch, MagicMock
from services.fit_parser import parse_fit_file
from datetime import datetime, timezone

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
        "total_elapsed_time": 2700.0,
        "total_distance": 8000.0,
        "avg_heart_rate": 148,
        "total_calories": 520,
        "sport": "running",
        "avg_speed": 2.96,
    })
    with patch("services.fit_parser.fitparse.FitFile") as MockFit:
        MockFit.return_value.get_messages.return_value = iter([session_msg])
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
        MockFit.return_value.get_messages.return_value = iter([session_msg])
        result = parse_fit_file(str(tmp_path / "cf.fit"))

    assert result["type"] == "crossfit"
    assert result["distance_km"] is None
    assert result["avg_pace"] is None

def test_no_session_message_raises(tmp_path):
    with patch("services.fit_parser.fitparse.FitFile") as MockFit:
        MockFit.return_value.get_messages.return_value = iter([])
        with pytest.raises(ValueError, match="No session message"):
            parse_fit_file(str(tmp_path / "empty.fit"))
