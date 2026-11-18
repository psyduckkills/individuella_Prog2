"""Hämtar och tolkar 3 dagarspprognoser från Open-Meteo

Filen innehåller två sorters kod:
-rena funktioner(hamta_stad ect.)
- en funktion som anropar API:et (hamta_prognos). Mockas i testerna
"""

import requests

FORECAST_url = "https://api.open-meteo.com/v1/forecast"
ANTAL_DAGAR = 3

STADER = {
    "stockholm": {"namn": "Stockholm", "lat": 59.33, "lon": 18.07},
    "goteborg": {"namn": "Göteborg", "lat": 57.71, "lon": 11.97},
    "malmo": {"namn": "Malmö", "lat": 55.61, "lon": 13.00},
    "umea": {"namn": "Umeå", "lat": 63.83, "lon": 20.26},
    "kiruna": {"namn": "Kiruna", "lat": 67.86, "lon": 20.23},
}

# WMO- väderkodder från Open-Meteos dokumentation

VADERKODER = {
    0: "Klart",
    1: "Mestadels klart",
    2: "Halvklart",
    3: "Mulet",
    45: "Dimma",
    48: "Rimfrostatdimma",
    51: "Lätt duggregn",
    53: "Duggregn",
    55: "Kraftigt duggregn",
    56: "Lätt regn",
    57: "Kraftigt duggregn",
    61: "Lätt regn",
    63: "Regn",
    65: "Kraftigt regn",
    71: "Lätt snöfall",
    73: "Snöfall",
    75: "Kraftigt snöfall",
    77: "Snökorn",
    80: "Lätta regnkurar",
    81: "Regnskurar",
    82: "Kraftiga regnskurar",
    85: "Lätta snöbyar",
    86: "Kraftiga snöbyar",
    95: "Åska",
    96: "Åska med lätt hagel",
    99: "Åska med kraftig hagel",
}


def vaderikon(kod):
    """Returnerar en ikon som passar väderkoden."""
    if kod == 0:
        return "☀️"
    if kod in (1, 2):
        return "⛅"
    if kod == 3:
        return "☁️"
    if kod in (45, 48):
        return "🌫️"
    if kod in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return "🌧️"
    if kod in (71, 73, 75, 77, 85, 86):
        return "❄️"
    if kod in (95, 96, 99):
        return "⛈️"
    return "❓"


# lånadkod

DAGNAMN = ["Idag", "Imorgon", "Övermorgon"]


class VaderApiFel(Exception):
    """Kastas när anropet mot API:et misslykas."""


def hamta_stad(stad):
    """Retunerar stadens namn och koordinater
    kastar ut ValueError om staden inte finns i STADER.
    """
    nyckel = str(stad).strip().lower()
    if nyckel not in STADER:
        raise ValueError(f"Okänd stad: {stad}")
    return STADER[nyckel]


def tolka_vaderkod(kod):
    """Översätter en WMO-väderkod"""
    return VADERKODER.get(kod, "Okänt väder")  # okänt väder = default värde


def dagnamn(index):
    """0 -> 'Idag',1 -> 'Imorgon', 2 -> 'Övermorgon'."""
    if isinstance(index, int) and 0 <= index < len(DAGNAMN):
        return DAGNAMN[index]
    raise ValueError(f"Ogiltigt dagindex {index}")


def tolka_prognos(data):
    """gör om API:ets JSON-svar till en lista med dictionary per dag."""
    try:
        daily = data["daily"]
        dagar = []
        for i, datum in enumerate(daily["time"][:ANTAL_DAGAR]):
            dagar.append(
                {
                    "dag": dagnamn(i),
                    "datum": datum,
                    "ikon": vaderikon(daily["weather_code"][i]),
                    "beskrivning": tolka_vaderkod(daily["weather_code"][i]),
                    "max": daily["temperature_2m_max"][i],
                    "min": daily["temperature_2m_min"][i],
                    "nederbord": daily["precipitation_sum"][i],
                }
            )
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError("Oväntat format på svaret från API:et") from e
    return dagar


# --------- API-anrop (mockas i testerna)------


def hamta_prognos(lat, lon, timeout=10):
    """Hämtar prognos för idag, imorgon och övermorgon från Open-Meteo"""
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Europe/Stockholm",
        "forecast_days": ANTAL_DAGAR,
    }
    try:
        svar = requests.get(FORECAST_url, params=params, timeout=timeout)
        svar.raise_for_status()
    except requests.Timeout as e:
        raise VaderApiFel("API:et svarade inte i tid") from e
    except requests.HTTPError as e:
        raise VaderApiFel(f"API:ET svarade med fel: {e}") from e
    except requests.RequestException as e:
        raise VaderApiFel("Kunde inte nå API:et") from e
    return svar.json()
