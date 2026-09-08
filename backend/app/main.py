import asyncio

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import ISK_CODE, SUPPORTED_CURRENCIES
from .models import AllRatesItem, ConvertRequest, ConvertResponse, CurrencyInfo
from .visa_client import VisaApiError, VisaConfigError, get_forex_rate

app = FastAPI(
    title="Gjaldmidlun FX API",
    description="Proxy for Visa's Foreign Exchange Rates API, ISK-based.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _extract_rate_and_amount(visa_response: dict) -> tuple[float, float]:
    rate = float(visa_response["conversionRate"])
    amount = float(visa_response["destinationAmount"])
    return rate, amount


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/currencies", response_model=list[CurrencyInfo])
async def currencies():
    return [
        CurrencyInfo(code=code, numeric_code=numeric)
        for code, numeric in SUPPORTED_CURRENCIES.items()
    ]


@app.post("/fx/convert", response_model=ConvertResponse)
async def convert(req: ConvertRequest):
    code = req.destination_currency.upper()
    if code not in SUPPORTED_CURRENCIES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported destination currency: {code}",
        )

    try:
        visa_response = await get_forex_rate(
            destination_currency_code=SUPPORTED_CURRENCIES[code],
            source_amount=req.source_amount,
            rate_product_code=req.rate_product_code,
        )
    except VisaConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except VisaApiError as exc:
        raise HTTPException(status_code=502, detail=exc.detail) from exc

    rate, amount = _extract_rate_and_amount(visa_response)

    return ConvertResponse(
        source_currency="ISK",
        destination_currency=code,
        source_amount=req.source_amount,
        destination_amount=amount,
        conversion_rate=rate,
        rate_product_code=req.rate_product_code,
    )


@app.get("/fx/all", response_model=list[AllRatesItem])
async def fx_all(
    source_amount: float = Query(1000, gt=0),
    rate_product_code: str = Query("A"),
):
    async def fetch_one(code: str, numeric: str) -> AllRatesItem:
        try:
            visa_response = await get_forex_rate(
                destination_currency_code=numeric,
                source_amount=source_amount,
                rate_product_code=rate_product_code,
            )
        except VisaConfigError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except VisaApiError as exc:
            return AllRatesItem(
                destination_currency=code,
                destination_amount=None,
                conversion_rate=None,
                error=exc.detail,
            )

        rate, amount = _extract_rate_and_amount(visa_response)
        return AllRatesItem(
            destination_currency=code,
            destination_amount=amount,
            conversion_rate=rate,
        )

    results = await asyncio.gather(
        *(fetch_one(code, numeric) for code, numeric in SUPPORTED_CURRENCIES.items())
    )
    return list(results)
