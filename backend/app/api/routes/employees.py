from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.employees import EmployeePage, EmployeeRead, SalaryUpdateRequest
from app.services.employees import (
    SalaryValidationError,
    UnsupportedCurrencyError,
    currency_minor_unit_exponent,
    list_employees,
    update_employee_salary,
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


@router.patch("/employees/{employee_id}/salary", response_model=EmployeeRead)
def patch_employee_salary(
    employee_id: str,
    request: SalaryUpdateRequest,
    session: Session = Depends(get_db),
) -> EmployeeRead:
    try:
        employee = update_employee_salary(
            session,
            employee_id=employee_id,
            salary_amount=request.salary_amount,
        )
    except (SalaryValidationError, UnsupportedCurrencyError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee