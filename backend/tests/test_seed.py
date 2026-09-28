from datetime import timezone
from decimal import Decimal

from sqlalchemy import func, select

from app.db.models import Employee
from app.db.seed import (
    CURRENCY_SALARY_RANGES,
    DEFAULT_EMPLOYEE_COUNT,
    FIXED_SEED_TIMESTAMP,
    generate_employees,
    seed_employees,
)
from app.services.employees import CURRENCY_MINOR_UNIT_EXPONENTS


def test_default_seed_creates_10000_employees(test_session_factory):
    with test_session_factory() as session:
        result_count = seed_employees(session)
        stored_count = session.scalar(select(func.count()).select_from(Employee))

    assert DEFAULT_EMPLOYEE_COUNT == 10_000
    assert result_count == 10_000
    assert stored_count == 10_000


def test_seeded_employee_ids_and_attributes_are_deterministic():
    first_run = generate_employees(40)
    second_run = generate_employees(40)

    def snapshot(employees):
        return [
            (
                employee.employee_id,
                employee.name,
                employee.country,
                employee.department,
                employee.salary_minor_units,
                employee.currency,
                employee.updated_at,
            )
            for employee in employees
        ]

    assert snapshot(first_run) == snapshot(second_run)


def test_seed_uses_supported_currencies_and_valid_salary_ranges():
    employees = generate_employees(300)

    assert {employee.country for employee in employees} == {"CA", "JP", "US"}
    assert len({employee.department for employee in employees}) > 1
    for employee in employees:
        assert employee.currency in CURRENCY_MINOR_UNIT_EXPONENTS
        assert isinstance(employee.salary_minor_units, int)
        assert employee.salary_minor_units >= 0
        exponent = CURRENCY_MINOR_UNIT_EXPONENTS[employee.currency]
        salary_major_units = Decimal(employee.salary_minor_units).scaleb(-exponent)
        minimum, maximum = CURRENCY_SALARY_RANGES[employee.currency]
        assert minimum <= salary_major_units <= maximum


def test_seeded_updated_at_is_a_fixed_utc_timestamp(test_session_factory):
    with test_session_factory() as session:
        seed_employees(session, count=5)
        timestamps = session.scalars(select(Employee.updated_at)).all()

    normalized_timestamps = [
        timestamp.replace(tzinfo=timezone.utc)
        if timestamp.tzinfo is None
        else timestamp.astimezone(timezone.utc)
        for timestamp in timestamps
    ]
    assert normalized_timestamps == [FIXED_SEED_TIMESTAMP] * 5


def test_running_seed_twice_does_not_create_duplicates(test_session_factory):
    with test_session_factory() as session:
        first_count = seed_employees(session, count=45)
        second_count = seed_employees(session, count=45)
        employee_ids = session.scalars(select(Employee.employee_id)).all()

    assert first_count == second_count == 45
    assert len(employee_ids) == len(set(employee_ids)) == 45