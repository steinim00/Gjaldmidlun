"""Thin client for Visa's Foreign Exchange Rates API.

Per Visa's own docs (developer.visa.com/capabilities/foreign_exchange/docs-authentication),
this API uses Two-Way SSL (mutual TLS) plus HTTP Basic Authentication with a
username/password issued alongside the client certificate — not X-Pay Token.
"""
from pathlib import Path

import httpx

from .config import (
    FOREX_RESOURCE_PATH,
    ISK_CODE,
    VISA_BASE_URL,
    VISA_CLIENT_CERT_PATH,
    VISA_CLIENT_KEY_PATH,
    VISA_PASSWORD,
    VISA_USER_ID,
)


class VisaConfigError(RuntimeError):
    pass


class VisaApiError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _format_source_amount(source_amount: float) -> str:
    """Format the request's sourceAmount per Visa's API schema (a decimal string).

    ISK has zero minor currency units (ISO 4217 exponent 0), so the amount is
    sent with no decimal point, e.g. "1000" rather than "1000.00".
    """
    return str(int(round(source_amount)))


async def get_forex_rate(
    destination_currency_code: str,
    source_amount: float,
    rate_product_code: str = "A",
) -> dict:
    """Call POST /forexrates/v2/foreignexchangerates for a single currency pair.

    ISK is always the source currency, per this service's scope.
    """
    if not VISA_USER_ID or not VISA_PASSWORD:
        raise VisaConfigError("VISA_USER_ID and VISA_PASSWORD must be set in the environment")

    if not Path(VISA_CLIENT_CERT_PATH).is_file() or not Path(VISA_CLIENT_KEY_PATH).is_file():
        raise VisaConfigError(
            "Visa client certificate/key not found at "
            f"{VISA_CLIENT_CERT_PATH} / {VISA_CLIENT_KEY_PATH}"
        )

    payload = {
        "destinationCurrencyCode": destination_currency_code,
        "sourceCurrencyCode": ISK_CODE,
        "sourceAmount": _format_source_amount(source_amount),
        "rateProductCode": rate_product_code,
    }

    url = f"{VISA_BASE_URL}{FOREX_RESOURCE_PATH}"

    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            cert=(VISA_CLIENT_CERT_PATH, VISA_CLIENT_KEY_PATH),
        ) as client:
            response = await client.post(
                url,
                json=payload,
                auth=(VISA_USER_ID, VISA_PASSWORD),
            )
    except httpx.HTTPError as exc:
        raise VisaApiError(502, f"Could not reach Visa API: {exc}") from exc

    if response.status_code >= 400:
        raise VisaApiError(response.status_code, response.text)

    return response.json()
