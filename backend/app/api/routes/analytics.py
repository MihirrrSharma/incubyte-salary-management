from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.analytics import CompensationAnalyticsResponse
from app.services.employees import UnsupportedCurrencyError
from app.services.analytics import get_compensation_analytics


router = APIRouter()


@router.get("/analytics/compensation", response_model=CompensationAnalyticsResponse)
def compensation_analytics(
    country: str | None = None,
    department: str | None = None,
    currency: str | None = Query(
        default=None,
        min_length=3,
        max_length=3,
        pattern="^[A-Z]{3}$",
    ),
    session: Session = Depends(get_db),
) -> CompensationAnalyticsResponse:
    try:
        return get_compensation_analytics(
            session,
            country=country,
            department=department,
            currency=currency,
        )
    except UnsupportedCurrencyError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error