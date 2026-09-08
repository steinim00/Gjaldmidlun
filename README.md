# Gjaldmiðlun

Vefþjónusta og einföld vefsíða sem sýnir gengi íslensku krónunnar (ISK)
gagnvart helstu erlendum gjaldmiðlum, byggt á **Foreign Exchange Rates API**
frá Visa (Visa Developer Center).

Verkefnið skiptist í tvennt:

- `backend/` – FastAPI þjónusta sem talar við Visa API og sér um auðkenningu
  (X-Pay Token).
- `frontend/` – Kyrrstæð HTML-síða sem sækir gögn frá bakendanum og birtir
  gengistöflu og reiknivél.

## Studdir gjaldmiðlar

ISK er alltaf grunngjaldmiðill (uppruni). Eftirfarandi gjaldmiðlar eru
studdir sem áfangagjaldmiðlar:

| Kóði | Gjaldmiðill        |
|------|---------------------|
| USD  | Bandaríkjadalur      |
| EUR  | Evra                 |
| GBP  | Sterlingspund        |
| DKK  | Dönsk króna          |
| NOK  | Norsk króna          |
| SEK  | Sænsk króna          |
| CAD  | Kanadadalur          |
| JPY  | Japanskt jen         |

## Að nálgast Visa aðgangslykla (X-Pay Token)

Þjónustan notar **X-Pay Token** auðkenningu (HMAC-SHA256), ekki Two-Way SSL.
Til að fá lykla:

1. Farðu inn á [Visa Developer Center](https://developer.visa.com) og
   skráðu þig inn eða stofnaðu aðgang.
2. Búðu til nýtt verkefni ("Project") og bættu við API-inu
   **Foreign Exchange Rates**.
3. Veldu auðkenningaraðferðina **X-Pay Token** (ekki Two-Way SSL/mTLS) þegar
   verkefnið er stofnað.
4. Farðu í **Credentials** flipann fyrir verkefnið. Þar finnur þú:
   - `API Key` (stundum kallað `User ID` eða birt í URL-inu sem `apiKey`)
   - `Shared Secret` sem er notað til að reikna út HMAC-SHA256 undirskrift
     fyrir hverja fyrirspurn.
5. Á meðan verkefnið er í sandkassa (`sandbox`) skal nota
   `https://sandbox.api.visa.com` sem grunn-URL. Þegar verkefnið er samþykkt
   fyrir framleiðslu (production) skiptir þú yfir í viðeigandi
   framleiðslu-URL sem Visa úthlutar.

**Aldrei** skrá þessa lykla beint í kóðann – þeir eru eingöngu lesnir úr
umhverfisbreytum (sjá `.env.example`).

## Uppsetning – bakendi (backend)

Krafist er Python 3.11 eða nýrra.

```bash
# 1. Búa til sýndarumhverfi (valfrjálst en mælt með)
python3 -m venv .venv
source .venv/bin/activate

# 2. Setja upp pakka
pip install -r requirements.txt

# 3. Afrita .env.example og fylla út með þínum Visa-lyklum
cp .env.example .env
# breyttu síðan .env og settu inn VISA_API_KEY og VISA_SHARED_SECRET

# 4. Keyra þjónustuna
uvicorn backend.app.main:app --reload --port 8000
```

Þjónustan keyrir þá á `http://localhost:8000`. Þú getur skoðað sjálfvirka
API-skjölun á `http://localhost:8000/docs`.

### Endapunktar

| Aðferð | Slóð             | Lýsing                                                        |
|--------|------------------|----------------------------------------------------------------|
| GET    | `/health`        | Athugar hvort þjónustan sé í gangi                             |
| GET    | `/currencies`    | Listi yfir studda áfangagjaldmiðla                             |
| POST   | `/fx/convert`    | Umreiknar tiltekna upphæð í ISK yfir í valinn gjaldmiðil        |
| GET    | `/fx/all`        | Sækir gengi allra studdra gjaldmiðla í einu (fyrir gengistöflu) |

Dæmi um `/fx/convert` beiðni:

```bash
curl -X POST http://localhost:8000/fx/convert \
  -H "Content-Type: application/json" \
  -d '{"destination_currency": "USD", "source_amount": 1000}'
```

Dæmi um `/fx/all`:

```bash
curl "http://localhost:8000/fx/all?source_amount=1000"
```

## Uppsetning – forsíða (frontend)

Forsíðan er ein kyrrstæð HTML-skrá sem sækir gögn í rauntíma frá bakendanum,
svo það þarf ekki að byggja hana sérstaklega.

```bash
cd frontend
python3 -m http.server 5500
```

Opnaðu síðan `http://localhost:5500` í vafra. Ef bakendinn keyrir á öðru
vistfangi en `http://localhost:8000`, má stilla það með því að setja
eftirfarandi í `<head>` á `index.html` áður en `<script>` keyrir:

```html
<script>window.API_BASE_URL = "http://localhost:8000";</script>
```

## Umhverfisbreytur

Sjá `.env.example`:

| Breyta                | Lýsing                                                        |
|------------------------|----------------------------------------------------------------|
| `VISA_API_KEY`         | API-lykill úr Visa Developer Center                            |
| `VISA_SHARED_SECRET`   | Deilt leyndarmál notað til að reikna X-Pay Token undirskrift    |
| `VISA_BASE_URL`        | Grunn-URL Visa API (sandbox eða production)                    |

`.env` skráin er í `.gitignore` og á aldrei að fara í útgáfustýringu.
