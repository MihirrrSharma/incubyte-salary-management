"""Seed synthetic employees. From the repository root run: python -m backend.app.db.seed."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import random
import sys

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session


if __package__ and __package__.startswith("backend."):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.db.models import Base, Employee
from app.db.session import SessionLocal, engine
from app.services.employees import currency_minor_unit_exponent


DEFAULT_EMPLOYEE_COUNT = 10_000
SEED_RANDOM_STATE = 1729
FIXED_SEED_TIMESTAMP = datetime(2025, 1, 1, tzinfo=timezone.utc)
COUNTRY_CURRENCIES = (("CA", "CAD"), ("JP", "JPY"), ("US", "USD"))
DEPARTMENTS = ("Engineering", "Finance", "HR", "Operations", "Product", "Sales")
CURRENCY_SALARY_RANGES = {
    "CAD": (45_000, 200_000),
    "JPY": (3_000_000, 20_000_000),
    "USD": (40_000, 200_000),
}


def generate_employees(count: int = DEFAULT_EMPLOYEE_COUNT) -> list[Employee]:
    if count < 0:
        raise ValueError("count must be non-negative")

    generator = random.Random(SEED_RANDOM_STATE)
    employees = []
    for number in range(1, count + 1):
        country, currency = generator.choice(COUNTRY_CURRENCIES)
        minimum_salary, maximum_salary = CURRENCY_SALARY_RANGES[currency]
        minor_unit_scale = 10 ** currency_minor_unit_exponent(currency)
        employees.append(
            Employee(
                employee_id=f"SYN{number:05d}",
                name=f"Fictional Employee {number:05d}",
                country=country,
                department=generator.choice(DEPARTMENTS),
                salary_minor_units=generator.randint(
                    minimum_salary * minor_unit_scale,
                    maximum_salary * minor_unit_scale,
                ),
                currency=currency,
                updated_at=FIXED_SEED_TIMESTAMP,
            )
        )
    return employees


def seed_employees(
    session: Session,
    count: int = DEFAULT_EMPLOYEE_COUNT,
) -> int:
    employees = generate_employees(count)
    employee_rows = [
        {
            "employee_id": employee.employee_id,
            "name": employee.name,
            "country": employee.country,
            "department": employee.department,
            "salary_minor_units": employee.salary_minor_units,
            "currency": employee.currency,
            "updated_at": employee.updated_at,
        }
        for employee in employees
    ]
    statement = sqlite_insert(Employee).on_conflict_do_nothing(
        index_elements=[Employee.employee_id]
    )

    try:
        session.execute(statement, employee_rows)
        session.commit()
    except Exception:
        session.rollback()
        raise

    return int(session.scalar(select(func.count()).select_from(Employee)) or 0)


def seed_if_empty(
    session: Session,
    count: int = DEFAULT_EMPLOYEE_COUNT,
) -> int:
    existing_count = int(
        session.scalar(select(func.count()).select_from(Employee)) or 0
    )
    if existing_count:
        return existing_count
    return seed_employees(session, count)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed synthetic salary-management employees")
    parser.add_argument("--count", type=int, default=DEFAULT_EMPLOYEE_COUNT)
    parser.add_argument(
        "--if-empty",
        action="store_true",
        help="seed only if the employee table contains no rows",
    )
    arguments = parser.parse_args()

    if arguments.count < 0:
        parser.error("--count must be non-negative")

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        if arguments.if_empty:
            employee_count = seed_if_empty(session, arguments.count)
        else:
            employee_count = seed_employees(session, arguments.count)
    print(f"Employee count: {employee_count}")


if __name__ == "__main__":
    main()