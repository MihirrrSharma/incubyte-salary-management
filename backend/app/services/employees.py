from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models import Employee
from app.db.queries import get_employee_page
from app.schemas.employees import EmployeePage, EmployeeRead


# Initial supported set; extend alongside the application's accepted employee data.
CURRENCY_MINOR_UNIT_EXPONENTS = {
    "CAD": 2,
    "JPY": 0,
    "USD": 2,
}


class UnsupportedCurrencyError(ValueError):
    pass


def currency_minor_unit_exponent(currency: str) -> int:
    try:
        return CURRENCY_MINOR_UNIT_EXPONENTS[currency]
    except KeyError as error:
        raise UnsupportedCurrencyError(
            f"Unsupported currency code: {currency}"
        ) from error


def format_salary_amount(salary_minor_units: int, currency: str) -> str:
    exponent = currency_minor_unit_exponent(currency)
    amount = Decimal(salary_minor_units).scaleb(-exponent)
    return f"{amount:.{exponent}f}"


def list_employees(
    session: Session,
    *,
    page: int,
    page_size: int,
    search: str | None,
    country: str | None,
    department: str | None,
    currency: str | None,
    sort_by: str,
    sort_order: str,
) -> EmployeePage:
    employees, total = get_employee_page(
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
    return EmployeePage(
        items=[
            EmployeeRead(
                employee_id=employee.employee_id,
                name=employee.name,
                country=employee.country,
                department=employee.department,
                salary_amount=format_salary_amount(
                    employee.salary_minor_units, employee.currency
                ),
                currency=employee.currency,
                updated_at=employee.updated_at,
            )
            for employee in employees
        ],
        total=total,
        page=page,
        page_size=page_size,
    )