import pytest

from applications import api


def test_startsida(client):
    svar = client.get("/")
    text = svar.get_data(as_text=True)
    assert svar.status_code == 200
    assert "Välj stad" in text


@pytest.mark.parametrize("namn", ["Stockholm", "Göteborg", "Malmö", "Umeå", "Kiruna"])
def test_startsida_visar_alla_stader(client, namn):
    assert namn in client.get("/").get_data(as_text=True)


@pytest.mark.parametrize(
    "url, namn",
    [
        ("/stockholm", "Stockholm"),
        ("/goteborg", "Göteborg"),
        ("/malmo", "Malmö"),
        ("/umea", "Umeå"),
        ("/kiruna", "Kiruna"),
    ],
)
def test_stad_lyckas(client, monkeypatch, exempeldata, url, namn):
    monkeypatch.setattr(api, "hamta_prognos", lambda *a, **k: exempeldata)

    svar = client.get(url)
    text = svar.get_data(as_text=True)

    assert svar.status_code == 200
    assert namn in text
    assert "Idag" in text
    assert "Övermorgon" in text
    assert "Lätt regn" in text


@pytest.mark.parametrize("url", ["/paris", "/london", "/123"])
def test_okand_stad(client, url):
    assert client.get(url).status_code == 404


def test_stad_api_timeout(client, monkeypatch):
    def kasta(*a, **k):
        raise api.VaderApiFel("API:et svarade inte i tid")

    monkeypatch.setattr(api, "hamta_prognos", kasta)

    svar = client.get("/stockholm")
    assert svar.status_code == 502
    assert "Kunde inte hämta väderdata" in svar.get_data(as_text=True)


def test_stad_trasigt_svar(client, monkeypatch):
    monkeypatch.setattr(api, "hamta_prognos", lambda *a, **k: {"fel": "format"})

    svar = client.get("/malmo")
    assert svar.status_code == 502
    assert "Oväntat format" in svar.get_data(as_text=True)
