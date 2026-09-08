"""Visa X-Pay Token generation (HMAC-SHA256 request signing).

Reference: Visa Developer Center - Two-Factor Authentication using
X-Pay Token, used as an alternative to Two-Way SSL/mutual TLS.

Token format:
    "xv2:" + timestamp + ":" + HMAC_SHA256(shared_secret, message)

where:
    message = timestamp + resource_path + query_string + body
"""
import hashlib
import hmac
import time


def generate_xpay_token(
    shared_secret: str,
    resource_path: str,
    query_string: str = "",
    body: str = "",
    timestamp: str | None = None,
) -> str:
    if timestamp is None:
        timestamp = str(int(time.time()))

    message = f"{timestamp}{resource_path}{query_string}{body}"
    digest = hmac.new(
        shared_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"xv2:{timestamp}:{digest}"
