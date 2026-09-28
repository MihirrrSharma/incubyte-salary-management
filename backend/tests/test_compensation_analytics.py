import pytest

from app.db.models import Employee


@pytest.fixture
def analytics_employees(test_session_factory):
    employees = [
        Employee(
            employee_id="U001",
            name="Alex One",
            country="US",
            department="Engineering",
            salary_minor_units=10000,
            currency="USD",
        ),
        Employee(
            employee_id="U002",
            name="Alex Two",
            country="US",
            department="Design",
            salary_minor_units=20000,
            currency="USD",
        ),
        Employee(
            employee_id="U003",
            name="Alex Three",
            country="US",
            department="Engineering",
            salary_minor_units=30000,
            currency="USD",
        ),
        Employee(
            employee_id="U004",
            name="Alex Four",
            country="US",
            department="HR",
            salary_minor_units=30000,
            currency="USD",
        ),
        Employee(
            employee_id="C001",
            name="Casey One",
            country="CA",
            department="Engineering",
            salary_minor_units=2000000,
            currency="CAD",
        ),
        Employee(
            employee_id="C002",
            name="Casey Two",
            country="CA",
            department="Sales",
            salary_minor_units=1000000,
            currency="CAD",
        ),
        Employee(
            employee_id="C003",
            name="Casey Three",
            country="CA",
            department="Engineering",
            salary_minor_units=2000000,
            currency="CAD",
        ),
        Employee(
            employee_id="J001",
            name="Jun One",
            country="JP",
            department="Engineering",
            salary_minor_units=10000000,
            currency="JPY",
        ),
    ]
    with test_session_factory() as session:
        session.add_all(employees)
        session.commit()
    return employees


def salary_groups(response_body):
    return {group["currency"]: group for group in response_body["salary_by_currency"]}


def test_returns_employee_count_for_filtered_cohort(client, analytics_employees):
    response = client.get("/api/analytics/compensation")

    assert response.status_code == 200
    assert response.json()["employee_count"] == 8


def test_returns_employee_counts_by_country(client, analytics_employees):
    response = client.get("/api/analytics/compensation")

    assert response.status_code == 200
    assert {
        group["country"]: group["employee_count"]
        for group in response.json()["employees_by_country"]
    } == {"CA": 3, "JP": 1, "US": 4}


def test_returns_employee_counts_by_department(client, analytics_employees):
    response = client.get("/api/analytics/compensation")

    assert response.status_code == 200
    assert {
        group["department"]: group["employee_count"]
        for group in response.json()["employees_by_department"]
    } == {"Design": 1, "Engineering": 5, "HR": 1, "Sales": 1}


def test_salary_metrics_are_grouped_by_currency(client, analytics_employees):
    response = client.get("/api/analytics/compensation")

    assert response.status_code == 200
    groups = salary_groups(response.json())
    assert set(groups) == {"CAD", "JPY", "USD"}
    assert {currency: group["employee_count"] for currency, group in groups.items()} == {
        "CAD": 3,
        "JPY": 1,
        "USD": 4,
    }


def test_average_salary_is_correct_per_currency(client, analytics_employees):
    response = client.get("/api/analytics/compensation")

    assert response.status_code == 200
    groups = salary_groups(response.json())
    assert groups["USD"]["average_salary"] == "225.00"
    assert groups["CAD"]["average_salary"] == "16666.67"
    assert groups["JPY"]["average_salary"] == "10000000"


def test_minimum_and_maximum_are_correct_per_currency(client, analytics_employees):
    response = client.get("/api/analytics/compensation")

    assert response.status_code == 200
    groups = salary_groups(response.json())
    assert (groups["USD"]["minimum_salary"], groups["USD"]["maximum_salary"]) == (
        "100.00",
        "300.00",
    )
    assert (groups["CAD"]["minimum_salary"], groups["CAD"]["maximum_salary"]) == (
        "10000.00",
        "20000.00",
    )


def test_odd_count_median_is_correct(client, analytics_employees):
    response = client.get("/api/analytics/compensation", params={"currency": "CAD"})

    assert response.status_code == 200
    assert salary_groups(response.json())["CAD"]["median_salary"] == "20000.00"


def test_even_count_median_is_average_of_middle_values(client, analytics_employees):
    response = client.get("/api/analytics/compensation", params={"currency": "USD"})

    assert response.status_code == 200
    assert salary_groups(response.json())["USD"]["median_salary"] == "250.00"


def test_equal_salaries_produce_a_single_distribution_bucket(client, analytics_employees):
    response = client.get(
        "/api/analytics/compensation",
        params={"country": "CA", "department": "Engineering"},
    )

    assert response.status_code == 200
    cad = salary_groups(response.json())["CAD"]
    assert cad["minimum_salary"] == cad["maximum_salary"] == "20000.00"
    assert cad["salary_distribution"] == [
        {
            "currency": "CAD",
            "minimum_salary": "20000.00",
            "maximum_salary": "20000.00",
            "employee_count": 2,
        }
    ]


def test_salary_distribution_uses_deterministic_ranges(client, analytics_employees):
    response = client.get("/api/analytics/compensation", params={"currency": "USD"})

    assert response.status_code == 200
    buckets = salary_groups(response.json())["USD"]["salary_distribution"]
    assert [
        (
            bucket["currency"],
            bucket["minimum_salary"],
            bucket["maximum_salary"],
            bucket["employee_count"],
        )
        for bucket in buckets
    ] == [
        ("USD", "100.00", "149.99", 1),
        ("USD", "150.00", "199.99", 0),
        ("USD", "200.00", "249.99", 1),
        ("USD", "250.00", "300.00", 2),
    ]


def test_country_filter_changes_the_cohort(client, analytics_employees):
    response = client.get("/api/analytics/compensation", params={"country": "US"})

    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 4
    assert body["employees_by_country"] == [{"country": "US", "employee_count": 4}]
    assert set(salary_groups(body)) == {"USD"}


def test_department_filter_changes_the_cohort(client, analytics_employees):
    response = client.get("/api/analytics/compensation", params={"department": "Sales"})

    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 1
    assert body["employees_by_department"] == [
        {"department": "Sales", "employee_count": 1}
    ]
    assert set(salary_groups(body)) == {"CAD"}


def test_currency_filter_restricts_the_cohort_and_salary_metrics(
    client,
    analytics_employees,
):
    response = client.get("/api/analytics/compensation", params={"currency": "CAD"})

    assert response.status_code == 200
    body = response.json()
    assert body["employee_count"] == 3
    assert set(salary_groups(body)) == {"CAD"}


def test_multiple_currencies_never_return_combined_salary_statistics(
    client,
    analytics_employees,
):
    response = client.get("/api/analytics/compensation")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "employee_count",
        "employees_by_country",
        "employees_by_department",
        "salary_by_currency",
    }
    assert {group["currency"] for group in body["salary_by_currency"]} == {
        "CAD",
        "JPY",
        "USD",
    }


def test_empty_filtered_cohort_returns_empty_groups(client, analytics_employees):
    response = client.get("/api/analytics/compensation", params={"country": "ZZ"})

    assert response.status_code == 200
    assert response.json() == {
        "employee_count": 0,
        "employees_by_country": [],
        "employees_by_department": [],
        "salary_by_currency": [],
    }