from unittest.mock import Mock

import pytest
import requests

from applications import api

# ------- Rena funktioner med parametrize -------


@pytest.mark.parametrize(
    "stad, namn",
    [
        ("stockholm", "Stockholm"),
        ("GOTEBORG", "Göteborg"),  # stora bokstäver
        ("   umea  ", "Umeå"),  # mellanslag runt
        ("kiruna", "Kiruna"),
    ],
)
def test_hamta_stad_giltig(stad, namn):
    assert api.hamta_stad(stad)["namn"] == namn


@pytest.mark.parametrize("stad", ["paris", "", None, 123, "uppsala"])
def test_hamta_stad_ogiltig(stad):
    with pytest.raises(ValueError):
        api.hamta_stad(stad)


@pytest.mark.parametrize(
    "kod, text",
    [
        (0, "Klart"),
        (63, "Regn"),
        (95, "Åska"),
        (999, "Okänt väder"),
        (None, "Okänt väder"),
    ],
)
def test_tolka_vaderkod(kod, text):
    assert api.tolka_vaderkod(kod) == text

@pytest.mark.parametrize("kod, ikon", [
    (0, "☀️"),
    (2, "⛅"),
    (3, "☁️"),
    (45, "🌫️"),
    (61, "🌧️"),
    (73, "❄️"),
    (95, "⛈️"),
    (999, "❓"),
])
def test_vaderikon(kod, ikon):
    assert api.vaderikon(kod) == ikon #lånad kod


@pytest.mark.parametrize(
    "index, namn",
    [
        (0, "Idag"),
        (1, "Imorgon"),
        (2, "Övermorgon"),
    ],
)
def test_dagnamn(index, namn):
    assert api.dagnamn(index) == namn


@pytest.mark.parametrize("index", [-1, 3, "1", None])
def test_dagnamn_ogiltigt(index):
    with pytest.raises(ValueError):
        api.dagnamn(index)


def test_tolka_prognos(exempeldata):
    dagar = api.tolka_prognos(exempeldata)
    assert len(dagar) == 3
    assert [d["dag"] for d in dagar] == ["Idag", "Imorgon", "Övermorgon"]
    assert dagar[1] == {
        "dag": "Imorgon",
        "datum": "2026-11-14",
        "beskrivning": "Lätt regn",
        "max": 4.5,
        "min": 0.3,
        "nederbord": 3.2,
    }


@pytest.mark.parametrize(
    "trasig_data",
    [
        {},  # inget "daily"
        {"daily": {"time": ["2026-11-18"]}},  # saknar temperaturer
    ],
)
def test_tolka_prognos_ogiltigt_svar(trasig_data):
    with pytest.raises(ValueError):
        api.tolka_prognos(trasig_data)


# --------- API-lagret, mockat(inget nätverk)----------


def test_hamta_vader_data_lyckas(monkeypatch, exempeldata):
    falskt_svar = Mock()
    falskt_svar.json.return_value = exempeldata
    mock_get = Mock(return_value=falskt_svar)
    monkeypatch.setattr(api.requests, "get", mock_get)

    data = api.hamta_prognos(59.33, 18.07)

    assert data == exempeldata
    mock_get.assert_called_once()
    params = mock_get.call_args.kwargs["params"]
    assert params["latitude"] == 59.33
    assert params["forecast_days"] == 3


def test_hamta_prognos_timeout(monkeypatch):
    monkeypatch.setattr(api.requests, "get", Mock(side_effect=requests.Timeout))

    with pytest.raises(api.VaderApiFel, match=" i tid"):
        api.hamta_prognos(59.33, 18.07)


def test_hamta_prognos_http_fel(monkeypatch):
    falskt_svar = Mock()
    falskt_svar.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
    monkeypatch.setattr(api.requests, "get", Mock(return_value=falskt_svar))

    with pytest.raises(api.VaderApiFel, match="500"):
        api.hamta_prognos(59.33, 18.07)


def test_hamta_prognos_ingen_anslutning(monkeypatch):
    monkeypatch.setattr(api.requests, "get", Mock(side_effect=requests.ConnectionError))

    with pytest.raises(api.VaderApiFel, match="nå API:et"):
        api.hamta_prognos(59.33, 18.07)
