from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.queries import (
    count_salary_in_range,
    get_compensation_summary,
    get_salary_middle_values,
)
from app.schemas.analytics import (
    CompensationAnalyticsResponse,
    EmployeeCountByCountry,
    EmployeeCountByDepartment,
    SalaryDistributionBucket,
    SalaryMetricsByCurrency,
)
from app.services.employees import (
    currency_minor_unit_exponent,
    format_salary_amount,
)


SALARY_DISTRIBUTION_BUCKET_COUNT = 4


def _salary_bucket_ranges(minimum: int, maximum: int) -> list[tuple[int, int]]:
    value_count = maximum - minimum + 1
    bucket_count = min(SALARY_DISTRIBUTION_BUCKET_COUNT, value_count)
    return [
        (
            minimum + value_count * index // bucket_count,
            minimum + value_count * (index + 1) // bucket_count - 1,
        )
        for index in range(bucket_count)
    ]


def get_compensation_analytics(
    session: Session,
    *,
    country: str | None,
    department: str | None,
    currency: str | None,
) -> CompensationAnalyticsResponse:
    if currency is not None:
        currency_minor_unit_exponent(currency)

    employee_count, country_counts, department_counts, salary_groups = (
        get_compensation_summary(
            session,
            country=country,
            department=department,
            currency=currency,
        )
    )
    salary_metrics = []
    for group_currency, count, total_minor_units, minimum, maximum in salary_groups:
        currency_minor_unit_exponent(group_currency)
        middle_values = get_salary_middle_values(
            session,
            country=country,
            department=department,
            currency=group_currency,
            offset=(count - 1) // 2,
            limit=2 if count % 2 == 0 else 1,
        )
        median_minor_units = Decimal(sum(middle_values)) / len(middle_values)

        buckets = []
        for bucket_minimum, bucket_maximum in _salary_bucket_ranges(minimum, maximum):
            bucket_count = count_salary_in_range(
                session,
                country=country,
                department=department,
                currency=group_currency,
                minimum_minor_units=bucket_minimum,
                maximum_minor_units=bucket_maximum,
            )
            buckets.append(
                SalaryDistributionBucket(
                    currency=group_currency,
                    minimum_salary=format_salary_amount(bucket_minimum, group_currency),
                    maximum_salary=format_salary_amount(bucket_maximum, group_currency),
                    employee_count=bucket_count,
                )
            )

        salary_metrics.append(
            SalaryMetricsByCurrency(
                currency=group_currency,
                employee_count=count,
                average_salary=format_salary_amount(
                    Decimal(total_minor_units) / count,
                    group_currency,
                ),
                median_salary=format_salary_amount(median_minor_units, group_currency),
                minimum_salary=format_salary_amount(minimum, group_currency),
                maximum_salary=format_salary_amount(maximum, group_currency),
                salary_distribution=buckets,
            )
        )

    return CompensationAnalyticsResponse(
        employee_count=employee_count,
        employees_by_country=[
            EmployeeCountByCountry(country=value, employee_count=count)
            for value, count in country_counts
        ],
        employees_by_department=[
            EmployeeCountByDepartment(department=value, employee_count=count)
            for value, count in department_counts
        ],
        salary_by_currency=salary_metrics,
    )