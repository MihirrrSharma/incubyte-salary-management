from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, StrictStr, field_validator


class EmployeeRead(BaseModel):
    employee_id: str
    name: str
    country: str
    department: str
    salary_amount: str
    currency: str
    updated_at: datetime

    @field_validator("updated_at", mode="before")
    @classmethod
    def normalize_updated_at_to_utc(cls, value: object) -> object:
        if not isinstance(value, datetime):
            return value
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class EmployeePage(BaseModel):
    items: list[EmployeeRead]
    total: int
    page: int
    page_size: int


class SalaryUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    salary_amount: StrictStr