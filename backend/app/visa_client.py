"""Thin client for Visa's Foreign Exchange Rates API."""
import json
from urllib.parse import urlencode

import httpx

from .config import (
    FOREX_RESOURCE_PATH,
    ISK_CODE,
    VISA_API_KEY,
    VISA_BASE_URL,
    VISA_SHARED_SECRET,
)
from .xpay import generate_xpay_token


class VisaConfigError(RuntimeError):
    pass


class VisaApiError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


async def get_forex_rate(
    destination_currency_code: str,
    source_amount: float,
    rate_product_code: str = "A",
) -> dict:
    """Call POST /forexrates/v2/foreignexchangerates for a single currency pair.

    ISK is always the source currency, per this service's scope.
    """
    if not VISA_API_KEY or not VISA_SHARED_SECRET:
        raise VisaConfigError(
            "VISA_API_KEY and VISA_SHARED_SECRET must be set in the environment"
        )

    query_params = {"apiKey": VISA_API_KEY}
    query_string = "?" + urlencode(query_params)

    payload = {
        "destinationCurrencyCode": destination_currency_code,
        "sourceCurrencyCode": ISK_CODE,
        "sourceAmount": source_amount,
        "rateProductCode": rate_product_code,
    }
    body = json.dumps(payload, separators=(",", ":"))

    xpay_token = generate_xpay_token(
        shared_secret=VISA_SHARED_SECRET,
        resource_path=FOREX_RESOURCE_PATH,
        query_string=query_string,
        body=body,
    )

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-pay-token": xpay_token,
    }

    url = f"{VISA_BASE_URL}{FOREX_RESOURCE_PATH}{query_string}"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, content=body, headers=headers)
    except httpx.HTTPError as exc:
        raise VisaApiError(502, f"Could not reach Visa API: {exc}") from exc

    if response.status_code >= 400:
        raise VisaApiError(response.status_code, response.text)

    return response.json()
