from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import re

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
MAX_SQLITE_INTEGER = 2**63 - 1
SALARY_AMOUNT_PATTERN = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)")


class UnsupportedCurrencyError(ValueError):
    pass


class SalaryValidationError(ValueError):
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


def salary_amount_to_minor_units(salary_amount: str, currency: str) -> int:
    exponent = currency_minor_unit_exponent(currency)
    if not SALARY_AMOUNT_PATTERN.fullmatch(salary_amount):
        raise SalaryValidationError("salary_amount must be a decimal string")

    try:
        amount = Decimal(salary_amount)
    except InvalidOperation as error:
        raise SalaryValidationError("salary_amount must be a valid decimal") from error

    if not amount.is_finite():
        raise SalaryValidationError("salary_amount must be finite")
    if amount.is_signed():
        raise SalaryValidationError("salary_amount must be non-negative")

    fractional_digits = max(0, -amount.as_tuple().exponent)
    if fractional_digits > exponent:
        raise SalaryValidationError(
            f"salary_amount supports at most {exponent} fractional digits for {currency}"
        )

    maximum_amount = Decimal(MAX_SQLITE_INTEGER).scaleb(-exponent)
    if amount > maximum_amount:
        raise SalaryValidationError("salary_amount exceeds the supported storage range")

    return int(amount.scaleb(exponent))


def employee_to_read(employee: Employee) -> EmployeeRead:
    return EmployeeRead(
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


def update_employee_salary(
    session: Session,
    *,
    employee_id: str,
    salary_amount: str,
) -> EmployeeRead | None:
    employee = session.get(Employee, employee_id)
    if employee is None:
        return None

    salary_minor_units = salary_amount_to_minor_units(
        salary_amount, employee.currency
    )
    employee.salary_minor_units = salary_minor_units
    employee.updated_at = datetime.now(timezone.utc)

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise

    session.refresh(employee)
    return employee_to_read(employee)


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
        items=[employee_to_read(employee) for employee in employees],
        total=total,
        page=page,
        page_size=page_size,
    )