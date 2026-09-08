"""Configuration loaded from environment variables."""
import os

from dotenv import load_dotenv

load_dotenv()

VISA_API_KEY = os.environ.get("VISA_API_KEY", "")
VISA_SHARED_SECRET = os.environ.get("VISA_SHARED_SECRET", "")
VISA_BASE_URL = os.environ.get("VISA_BASE_URL", "https://sandbox.api.visa.com")

FOREX_RESOURCE_PATH = "/forexrates/v2/foreignexchangerates"

# ISO 4217 numeric currency codes.
ISK_CODE = "352"

SUPPORTED_CURRENCIES = {
    "USD": "840",
    "EUR": "978",
    "GBP": "826",
    "DKK": "208",
    "NOK": "578",
    "SEK": "752",
    "CAD": "124",
    "JPY": "392",
}
