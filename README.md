# Gjaldmiðlun

Vefþjónusta og einföld vefsíða sem sýnir gengi íslensku krónunnar (ISK)
gagnvart helstu erlendum gjaldmiðlum, byggt á **Foreign Exchange Rates API**
frá Visa (Visa Developer Center).

Verkefnið skiptist í tvennt:

- `backend/` – FastAPI þjónusta sem talar við Visa API og sér um auðkenningu
  (Two-Way SSL / gagnkvæm TLS-tenging).
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

## Að nálgast Visa aðgangslykla (Two-Way SSL)

Samkvæmt opinberum gögnum Visa
([Foreign Exchange Authentication Method](https://developer.visa.com/capabilities/foreign_exchange/docs-authentication))
notar **Foreign Exchange Rates API** eingöngu **Two-Way SSL** (gagnkvæma
TLS-tengingu), ekki X-Pay Token. Til að fá aðgang:

1. Farðu inn á [Visa Developer Center](https://developer.visa.com) og
   skráðu þig inn eða stofnaðu aðgang.
2. Búðu til nýtt verkefni ("Project") og bættu við API-inu
   **Foreign Exchange Rates**.
3. Í verkefninu, farðu í **Credentials → Two-Way SSL → Inbound** og smelltu
   á **Add CSR**. Þú þarft að útbúa CSR (Certificate Signing Request) og
   samsvarandi einkalykil (private key) fyrst, t.d. með:

   ```bash
   openssl req -new -newkey rsa:2048 -nodes \
     -keyout certs/visa_private_key.pem \
     -out certs/visa_csr.pem \
     -subj "/C=IS/ST=<hérað>/L=<staður>/O=<fyrirtæki>/OU=<deild>/CN=<heiti>"
   ```

   Öll reitirnir (C, ST, L, O, OU, CN) þurfa að vera útfylltir, annars
   hafnar Visa CSR-inu. Skráin þarf að heita `<eitthvað>.csr` eða
   `<eitthvað>.pem` (nákvæmlega einn punktur í skráarheitinu) þegar hún er
   hlaðið upp.
4. Þegar Visa hefur samþykkt CSR-ið færðu útgefið vottorð (certificate) til
   að hlaða niður, ásamt notandanafni (`User ID`) og lykilorði
   (`Password`) sem fylgja vottorðinu.
5. Vistaðu vottorðið sem `certs/visa_cert.pem` við hliðina á einkalyklinum
   (`certs/visa_private_key.pem`). Mappan `certs/` er í `.gitignore` –
   þessar skrár eiga **aldrei** að fara í útgáfustýringu.
6. Á meðan verkefnið er í sandkassa (`sandbox`) skal nota
   `https://sandbox.api.visa.com` sem grunn-URL. Þegar verkefnið er samþykkt
   fyrir framleiðslu (production) skiptir þú yfir í viðeigandi
   framleiðslu-URL sem Visa úthlutar.

**Aldrei** skrá `User ID`, `Password` eða vottorðsskrárnar beint í kóðann –
þau eru eingöngu lesin úr umhverfisbreytum og skráarslóðum (sjá
`.env.example`).

## Uppsetning – bakendi (backend)

Krafist er Python 3.11 eða nýrra.

```bash
# 1. Búa til sýndarumhverfi (valfrjálst en mælt með)
python3 -m venv .venv
source .venv/bin/activate

# 2. Setja upp pakka
pip install -r requirements.txt

# 3. Afrita .env.example og fylla út með þínum Visa-upplýsingum
cp .env.example .env
# breyttu síðan .env og settu inn VISA_USER_ID og VISA_PASSWORD,
# og gakktu úr skugga um að certs/visa_cert.pem og
# certs/visa_private_key.pem séu til staðar (sjá kaflann hér að ofan)

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

Opnaðu síðan `http://localhost:5500` í vafra. Til að tengja hana við
lifandi bakenda (t.d. þann sem keyrir á `http://localhost:8000` hér að
ofan) skal setja eftirfarandi í `<head>` á `index.html` áður en
`<script>` keyrir:

```html
<script>window.API_BASE_URL = "http://localhost:8000";</script>
```

Ef `API_BASE_URL` er ekki stillt les síðan í staðinn úr `rates.json` í
sömu möppu (sjá næsta kafla um GitHub Pages).

## Útgáfa á GitHub Pages

GitHub Pages hýsir eingöngu kyrrstæðar skrár, svo bakendinn (FastAPI) getur
ekki keyrt þar. Til að birta síðuna samt á Pages er notuð eftirfarandi
lausn:

- Vinnuferli í GitHub Actions (`.github/workflows/deploy-pages.yml`) keyrir
  á klukkutíma fresti (og við hverja `push` á `main`). Það sækir núverandi
  gengi með `scripts/fetch_rates.py` og býr til `frontend/rates.json`.
- Forsíðan les sjálfkrafa úr `rates.json` þegar `window.API_BASE_URL` er
  ekki stillt, og reiknar umreikninga í vafranum út frá vistuðu gengi.
  Þannig þarf enginn lifandi bakendi að keyra fyrir Pages-útgáfuna, og
  Visa-lyklarnir fara aldrei í vafra notandans.
- Þegar `API_BASE_URL` er stillt (t.d. með sjálfhýstum bakenda) notar
  síðan þess í stað `GET /fx/all` og `POST /fx/convert` í rauntíma, eins og
  lýst er hér að ofan.

### Uppsetning

1. Í `Settings → Secrets and variables → Actions` fyrir GitHub-safnið skal
   bæta við leynilyklunum `VISA_USER_ID`, `VISA_PASSWORD`, `VISA_BASE_URL`,
   og `VISA_CLIENT_CERT` / `VISA_CLIENT_KEY` (innihald `visa_cert.pem` og
   `visa_private_key.pem`, límt inn sem margra-lína leynilykill).
2. Í `Settings → Pages` skal velja **Source: GitHub Actions**.
3. Keyra vinnuferlið handvirkt í fyrsta sinn (`Actions → Deploy Pages → Run
   workflow`), eða einfaldlega `push`-a á `main` – þá keyrir það sjálfkrafa.
4. Síðan birtist á slóðinni sem GitHub Pages úthlutar safninu.

## Umhverfisbreytur

Sjá `.env.example`:

| Breyta                   | Lýsing                                                     |
|--------------------------|-------------------------------------------------------------|
| `VISA_USER_ID`           | Notandanafn sem fylgir Two-Way SSL vottorðinu                |
| `VISA_PASSWORD`          | Lykilorð sem fylgir Two-Way SSL vottorðinu                   |
| `VISA_CLIENT_CERT_PATH`  | Slóð á útgefið vottorð (sjálfgefið `certs/visa_cert.pem`)    |
| `VISA_CLIENT_KEY_PATH`   | Slóð á einkalykil (sjálfgefið `certs/visa_private_key.pem`)  |
| `VISA_BASE_URL`          | Grunn-URL Visa API (sandbox eða production)                  |

`.env` skráin og `certs/` mappan eru í `.gitignore` og eiga aldrei að fara
í útgáfustýringu.
