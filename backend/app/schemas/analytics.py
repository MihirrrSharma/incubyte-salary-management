from pydantic import BaseModel


class EmployeeCountByCountry(BaseModel):
    country: str
    employee_count: int


class EmployeeCountByDepartment(BaseModel):
    department: str
    employee_count: int


class SalaryDistributionBucket(BaseModel):
    currency: str
    minimum_salary: str
    maximum_salary: str
    employee_count: int


class SalaryMetricsByCurrency(BaseModel):
    currency: str
    employee_count: int
    average_salary: str
    median_salary: str
    minimum_salary: str
    maximum_salary: str
    salary_distribution: list[SalaryDistributionBucket]


class CompensationAnalyticsResponse(BaseModel):
    employee_count: int
    employees_by_country: list[EmployeeCountByCountry]
    employees_by_department: list[EmployeeCountByDepartment]
    salary_by_currency: list[SalaryMetricsByCurrency]