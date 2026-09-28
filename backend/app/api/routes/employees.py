from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.employees import EmployeePage
from app.services.employees import (
    UnsupportedCurrencyError,
    currency_minor_unit_exponent,
    list_employees,
)


router = APIRouter()
SortField = Literal["employee_id", "name", "country", "department", "salary", "updated_at"]
SortOrder = Literal["asc", "desc"]


@router.get("/employees", response_model=EmployeePage)
def get_employees(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1),
    country: str | None = None,
    department: str | None = None,
    currency: str | None = Query(default=None, min_length=3, max_length=3, pattern="^[A-Z]{3}$"),
    sort_by: SortField = "employee_id",
    sort_order: SortOrder = "asc",
    session: Session = Depends(get_db),
) -> EmployeePage:
    if sort_by == "salary" and currency is None:
        raise HTTPException(
            status_code=422,
            detail="currency is required when sorting by salary",
        )
    try:
        if currency is not None:
            currency_minor_unit_exponent(currency)
        return list_employees(
            session,
            page=page,
            page_size=page_size,
            search=search,
            country=country,
            department=department,
            currency=currency,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except UnsupportedCurrencyError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error