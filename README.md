# Väder 3 Dagar Prognos

En Flask-app som visar väderprognosen för idag, imorgon och övermorgon i fem svenska städer: Stockholm, Göteborg, Malmö, Umeå och Kiruna. Väderdatan hämtas från [Open-Meteo](https://open-meteo.com/).

## Projektstruktur

```
individuella_Prog2/
├── main.py                 # Flask-appen och dess routes
├── pytest.ini              # Inställningar för pytest
├── requirements.txt        # Paket som behövs
├── applications/
│   ├── __init__.py
│   └── api.py              # API-anrop och rena funktioner
├── templates/
│   ├── base.html           # Grundmall som de andra ärver från
│   ├── startsida.html      # Startsida med val av stad
│   └── stad.html           # En mall för alla fem städer
├── static/
│   └── colorCloud.gif      # Bakgrundsbild
└── tests/
    ├── conftest.py         # Fixtures (Flasks testklient och exempeldata)
    ├── test_api.py         # Tester för funktionerna i api.py
    └── test_main.py        # Tester för routes med Flasks testklient
```

## Installation

Kräver Python 3.10 eller senare.

```bash
git clone https://github.com/psyduckkills/individuella_Prog2.git
cd individuella_Prog2

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

python -m pip install -r requirements.txt
```

## Köra appen

```
python main.py
```

Öppna sedan **http://127.0.0.1:5000** i webbläsaren och välj en stad i menyn. Appen behöver internetanslutning för att hämta prognosen. Stoppa servern med `Ctrl + C`.

## Köra testerna

```
python -m pytest -v
```

Testerna körs helt utan nätverk eftersom alla anrop mot API:et är mockade.

## Frågor och svar

### 1. Varför mockar du anropen mot API:et i dina tester, och vad skulle hända om du inte gjorde det?

Jag mockar anropen för att testerna ska vara snabba, ge samma resultat varje gång och fungera utan internet. I `test_api.py` byter jag ut `requests.get` mot en `Mock` med `monkeypatch`, och i `test_main.py` byter jag ut `api.hamta_prognos` så att routen får datan från fixturen `exempeldata` i `conftest.py`. Utan mockning skulle testerna bero på det riktiga vädret, som ändras varje dag, så det skulle inte gå att skriva fasta förväntade värden. De skulle också misslyckas om nätverket eller Open-Meteo låg nere, och det vore nästan omöjligt att testa felfall som timeout och HTTP-fel på beställning.

### 2. Vad gör timeout och raise_for_status(), och varför behövs de?

`timeout=10` i `hamta_prognos` gör att `requests.get` ger upp och kastar `requests.Timeout` om API:et inte svarat inom tio sekunder. Utan den kan anropet hänga för evigt och användaren får bara en sida som laddar. `raise_for_status()` kastar `requests.HTTPError` om servern svarar med en felkod som 400 eller 500, eftersom `requests` annars behandlar även felsvar som lyckade. I `hamta_prognos` fångar jag båda felen och kastar istället mitt eget `VaderApiFel`, så att routen i `main.py` kan visa ett tydligt felmeddelande med statuskod 502 istället för att krascha.

### 3. Hur fungerar mallarv i Jinja2? Förklara med exempel från dina egna mallar.

Med mallarv skriver man den gemensamma strukturen en gång i en grundmall och låter andra mallar fylla i delar av den. Min `base.html` innehåller `<head>`, Bootstrap, bakgrundsbilden och footern med licensen, samt två tomma block: `{% block title %}` och `{% block content %}`. Både `startsida.html` och `stad.html` börjar med `{% extends "base.html" %}` och fyller sedan i blocken, till exempel lägger `startsida.html` dropdown-menyn i `content` och `stad.html` lägger prognoskorten där. Allt i en barnmall som ligger utanför ett block ignoreras, och blocknamnen måste vara exakt samma i båda mallarna för att innehållet ska hamna rätt.

## Källa och licens för väderdata

Väderdata från [Open-Meteo.com](https://open-meteo.com/), licensierad under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.sv).