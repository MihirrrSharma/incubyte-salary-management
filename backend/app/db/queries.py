from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Employee


SORT_COLUMNS = {
    "employee_id": Employee.employee_id,
    "name": Employee.name,
    "country": Employee.country,
    "department": Employee.department,
    "salary": Employee.salary_minor_units,
    "updated_at": Employee.updated_at,
}


def get_employee_page(
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
) -> tuple[list[Employee], int]:
    filters = []
    if search:
        filters.append(
            or_(
                Employee.employee_id.ilike(f"{search}%"),
                Employee.name.ilike(f"%{search}%"),
            )
        )
    if country is not None:
        filters.append(Employee.country == country)
    if department is not None:
        filters.append(Employee.department == department)
    if currency is not None:
        filters.append(Employee.currency == currency)

    total = session.scalar(
        select(func.count()).select_from(Employee).where(*filters)
    ) or 0

    sort_column = SORT_COLUMNS[sort_by]
    primary_order = sort_column.desc() if sort_order == "desc" else sort_column.asc()
    order_by = [primary_order]
    if sort_by != "employee_id":
        order_by.append(Employee.employee_id.asc())

    employees = session.scalars(
        select(Employee)
        .where(*filters)
        .order_by(*order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(employees), total


def _analytics_filters(
    *, country: str | None, department: str | None, currency: str | None
):
    filters = []
    if country is not None:
        filters.append(Employee.country == country)
    if department is not None:
        filters.append(Employee.department == department)
    if currency is not None:
        filters.append(Employee.currency == currency)
    return filters


def get_compensation_summary(
    session: Session,
    *,
    country: str | None,
    department: str | None,
    currency: str | None,
) -> tuple[
    int,
    list[tuple[str, int]],
    list[tuple[str, int]],
    list[tuple[str, int, int, int, int]],
]:
    filters = _analytics_filters(
        country=country,
        department=department,
        currency=currency,
    )
    employee_count = session.scalar(
        select(func.count(Employee.employee_id)).where(*filters)
    ) or 0
    country_counts = [
        (str(value), int(count))
        for value, count in session.execute(
            select(Employee.country, func.count(Employee.employee_id))
            .where(*filters)
            .group_by(Employee.country)
            .order_by(Employee.country)
        )
    ]
    department_counts = [
        (str(value), int(count))
        for value, count in session.execute(
            select(Employee.department, func.count(Employee.employee_id))
            .where(*filters)
            .group_by(Employee.department)
            .order_by(Employee.department)
        )
    ]
    salary_groups = [
        (str(group_currency), int(count), int(total), int(minimum), int(maximum))
        for group_currency, count, total, minimum, maximum in session.execute(
            select(
                Employee.currency,
                func.count(Employee.employee_id),
                func.sum(Employee.salary_minor_units),
                func.min(Employee.salary_minor_units),
                func.max(Employee.salary_minor_units),
            )
            .where(*filters)
            .group_by(Employee.currency)
            .order_by(Employee.currency)
        )
    ]
    return int(employee_count), country_counts, department_counts, salary_groups


def get_salary_middle_values(
    session: Session,
    *,
    country: str | None,
    department: str | None,
    currency: str,
    offset: int,
    limit: int,
) -> list[int]:
    filters = _analytics_filters(
        country=country,
        department=department,
        currency=currency,
    )
    values = session.scalars(
        select(Employee.salary_minor_units)
        .where(*filters)
        .order_by(Employee.salary_minor_units, Employee.employee_id)
        .offset(offset)
        .limit(limit)
    ).all()
    return list(values)


def count_salary_in_range(
    session: Session,
    *,
    country: str | None,
    department: str | None,
    currency: str,
    minimum_minor_units: int,
    maximum_minor_units: int,
) -> int:
    filters = _analytics_filters(
        country=country,
        department=department,
        currency=currency,
    )
    filters.extend(
        (
            Employee.salary_minor_units >= minimum_minor_units,
            Employee.salary_minor_units <= maximum_minor_units,
        )
    )
    return int(
        session.scalar(
            select(func.count(Employee.employee_id)).where(*filters)
        )
        or 0
    )