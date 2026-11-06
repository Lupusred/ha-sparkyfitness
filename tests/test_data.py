import pytest

from custom_components.sparkyfitness.data import number, parse_snapshot


@pytest.mark.parametrize("value", [None, True, False, "", "nan", "inf", {}, [], "bad"])
def test_invalid_number(value):
    assert number(value) is None


def test_values(snapshot):
    data = parse_snapshot(snapshot)
    assert data["protein"].value == 35
    assert data["protein_goal"].value == 110
    assert data["calories_remaining"].value == 1600
    assert data["weight"].unit == "kg"
    assert data["weight"].value == 80.2
    assert data["training_duration"].value == 40
    assert data["custom_arm"].value == 32.5
    assert data["custom_arm"].date == "2026-11-04"
    assert data["sleep_time_asleep_in_seconds"].value == 27000
    assert data["sodium"].value is None


def test_missing_and_bad_data(snapshot):
    snapshot["summary"]["foodEntries"][0]["serving_size"] = 0
    snapshot["body"]["weight"] = "bad"
    data = parse_snapshot(snapshot)
    assert data["protein"].value is None
    assert data["weight"].value is None
    assert "body_fat_percentage" not in data
    assert parse_snapshot({"day": "2026-11-05"}) == {}


def test_daily_custom_latest_and_rename(snapshot):
    snapshot["categories"][0].update(frequency="Daily", display_name="Renamed")
    assert parse_snapshot(snapshot)["custom_arm"].value is None
    snapshot["custom"] += [
        {
            "category_id": "arm",
            "value": 10,
            "entry_date": "2026-11-05",
            "entry_timestamp": "2026-11-05T10:00:00Z",
        },
        {
            "category_id": "arm",
            "value": 20,
            "entry_date": "2026-11-05",
            "entry_timestamp": "2026-11-05T11:00:00Z",
        },
    ]
    assert parse_snapshot(snapshot)["custom_arm"].value == 20
    assert parse_snapshot(snapshot)["custom_arm"].name == "Renamed"


def test_empty_day_and_sleep_overlap(snapshot):
    snapshot["summary"]["foodEntries"] = []
    snapshot["summary"]["supplementTotals"] = {}
    snapshot["sleep"].append({"entry_date": "2026-11-05", "duration_in_seconds": 1000})
    assert parse_snapshot(snapshot)["protein"].value == 0
    assert parse_snapshot(snapshot)["sleep_duration_in_seconds"].value == 28800


def test_text_category(snapshot):
    snapshot["categories"][0]["data_type"] = "text"
    snapshot["custom"][0]["value"] = "Rested"
    reading = parse_snapshot(snapshot)["custom_arm"]
    assert reading.value == "Rested" and reading.unit is None and not reading.numeric
