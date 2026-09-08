"""Fetches ISK exchange rates from Visa and writes a static snapshot for GitHub Pages.

Run from the repo root: python scripts/fetch_rates.py
Writes frontend/rates.json, which the static frontend reads when it is not
configured against a live backend (see frontend/index.html).
"""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.app.config import SUPPORTED_CURRENCIES  # noqa: E402
from backend.app.visa_client import (  # noqa: E402
    VisaApiError,
    VisaConfigError,
    get_forex_rate,
)

OUTPUT_PATH = REPO_ROOT / "frontend" / "rates.json"
SOURCE_AMOUNT = 1000


async def fetch_one(code: str, numeric: str) -> dict:
    try:
        visa_response = await get_forex_rate(numeric, SOURCE_AMOUNT)
    except (VisaApiError, VisaConfigError) as exc:
        return {
            "destination_currency": code,
            "destination_amount": None,
            "conversion_rate": None,
            "error": str(exc),
        }

    return {
        "destination_currency": code,
        "destination_amount": float(visa_response["destinationAmount"]),
        "conversion_rate": float(visa_response["conversionRate"]),
        "error": None,
    }


async def fetch_all() -> list[dict]:
    return list(
        await asyncio.gather(
            *(fetch_one(code, numeric) for code, numeric in SUPPORTED_CURRENCIES.items())
        )
    )


def main() -> None:
    rates = asyncio.run(fetch_all())
    payload = {
        "source_currency": "ISK",
        "source_amount": SOURCE_AMOUNT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rates": rates,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
