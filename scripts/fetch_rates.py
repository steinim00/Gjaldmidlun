"""Fetches ISK exchange rates from the Frankfurter API and writes a static
snapshot for GitHub Pages.

Run from the repo root: python scripts/fetch_rates.py
Writes frontend/rates.json, which the static frontend reads when it is not
configured against a live backend (see frontend/index.html).

Frankfurter (https://frankfurter.dev) publishes real, ECB-sourced daily
exchange rates and includes ISK, with no API key or account required. This
replaces the Visa sandbox as the data source for the deployed static site,
since the sandbox returns internally-inconsistent test fixtures rather than
real rates (destinationAmount and conversionRate don't satisfy the API's own
documented relationship). The self-hosted FastAPI backend still supports
live Visa Two-Way SSL card rates for anyone with production Visa access —
see backend/app/visa_client.py — this script only affects the static
GitHub Pages snapshot.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "frontend" / "rates.json"
SOURCE_AMOUNT = 1000

FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"
SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "DKK", "NOK", "SEK", "CAD", "JPY"]


def fetch_all() -> list[dict]:
    params = {"base": "ISK", "symbols": ",".join(SUPPORTED_CURRENCIES)}

    try:
        response = httpx.get(FRANKFURTER_URL, params=params, timeout=15.0)
        response.raise_for_status()
        rates = response.json()["rates"]
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        error = f"Could not reach Frankfurter API: {exc}"
        return [
            {
                "destination_currency": code,
                "destination_amount": None,
                "conversion_rate": None,
                "error": error,
            }
            for code in SUPPORTED_CURRENCIES
        ]

    results = []
    for code in SUPPORTED_CURRENCIES:
        rate = rates.get(code)
        if rate is None:
            results.append(
                {
                    "destination_currency": code,
                    "destination_amount": None,
                    "conversion_rate": None,
                    "error": f"{code} not returned by Frankfurter",
                }
            )
        else:
            results.append(
                {
                    "destination_currency": code,
                    "destination_amount": SOURCE_AMOUNT * rate,
                    "conversion_rate": rate,
                    "error": None,
                }
            )
    return results


def main() -> None:
    rates = fetch_all()
    payload = {
        "source_currency": "ISK",
        "source_amount": SOURCE_AMOUNT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Frankfurter (ECB-sourced daily reference rates)",
        "rates": rates,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
