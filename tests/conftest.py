"""Synthetic fixtures only; no production server access."""

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def custom_components(enable_custom_integrations):
    yield


@pytest.fixture
def snapshot():
    return {
        "day": "2026-11-05",
        "summary": {
            "calorieBalance": {"eaten": 600, "goal": 2000, "remaining": 1600, "burned": 200},
            "goals": {"protein": 100, "carbs": 250, "fat": 70},
            "adjustedGoals": {"protein": 110},
            "foodEntries": [
                {"protein": 20, "carbs": 30, "fat": 10, "quantity": 150, "serving_size": 100}
            ],
            "supplementTotals": {"protein": 5, "carbs": 0, "fat": 0},
            "exerciseSessions": [
                {"type": "preset", "total_duration_minutes": 30},
                {"type": "individual", "duration_minutes": 10},
            ],
            "waterIntake": 500,
        },
        "body": {"weight": "80.2", "steps": 5000, "waist": 90},
        "categories": [
            {
                "id": "arm",
                "name": "Left arm",
                "measurement_type": "cm",
                "frequency": "All",
                "data_type": "numeric",
            }
        ],
        "custom": [{"category_id": "arm", "value": "32.5", "entry_date": "2026-11-04"}],
        "sleep": [
            {
                "entry_date": "2026-11-05",
                "duration_in_seconds": 28800,
                "time_asleep_in_seconds": 27000,
            }
        ],
    }
