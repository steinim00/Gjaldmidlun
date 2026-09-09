"""Configuration loaded from environment variables."""
import os

from dotenv import load_dotenv

load_dotenv()

# Two-Way SSL (mutual TLS) credentials, per Visa's Foreign Exchange Rates
# API authentication requirements: a client certificate/key pair plus a
# username/password issued alongside it when the certificate is generated.
VISA_USER_ID = os.environ.get("VISA_USER_ID", "")
VISA_PASSWORD = os.environ.get("VISA_PASSWORD", "")
VISA_CLIENT_CERT_PATH = os.environ.get("VISA_CLIENT_CERT_PATH", "certs/visa_cert.pem")
VISA_CLIENT_KEY_PATH = os.environ.get(
    "VISA_CLIENT_KEY_PATH", "certs/visa_private_key.pem"
)
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
