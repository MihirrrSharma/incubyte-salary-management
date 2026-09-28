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