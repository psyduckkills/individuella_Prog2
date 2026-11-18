import pytest

from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def exempeldata():
    """Ser ut som riktig Json-svar från Open-Meteo (daily, 3 dagar)."""
    return {
        "daily": {
            "time": ["2026-11-13", "2026-11-14", "2026-11-15"],
            "weather_code": [3, 61, 0],
            "temperature_2m_max": [6.1, 4.5, 3.0],
            "temperature_2m_min": [1.2, 0.3, -2.4],
            "precipitation_sum": [0.0, 3.2, 0.0],
        }
    }
