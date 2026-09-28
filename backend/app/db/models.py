from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("salary_minor_units >= 0", name="ck_employees_salary_nonnegative"),
        CheckConstraint("length(currency) = 3", name="ck_employees_currency_length"),
        Index("ix_employees_country", "country"),
        Index("ix_employees_department", "department"),
        Index("ix_employees_currency_salary", "currency", "salary_minor_units"),
    )

    employee_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str] = mapped_column(String, nullable=False)
    salary_minor_units: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )