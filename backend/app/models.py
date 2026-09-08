from pydantic import BaseModel, Field


class ConvertRequest(BaseModel):
    destination_currency: str = Field(
        ..., description="Three-letter destination currency code, e.g. USD"
    )
    source_amount: float = Field(..., gt=0, description="Amount in ISK to convert")
    rate_product_code: str = Field(
        default="A", description="Visa rate product code (A = card-based rates)"
    )


class ConvertResponse(BaseModel):
    source_currency: str
    destination_currency: str
    source_amount: float
    destination_amount: float
    conversion_rate: float
    rate_product_code: str


class CurrencyInfo(BaseModel):
    code: str
    numeric_code: str


class AllRatesItem(BaseModel):
    destination_currency: str
    destination_amount: float | None
    conversion_rate: float | None
    error: str | None = None
