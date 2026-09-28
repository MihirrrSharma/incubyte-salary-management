from datetime import datetime, timedelta, timezone

import pytest

from app.db.models import Employee
from app.schemas.employees import EmployeeRead


def test_returns_employees_with_pagination_metadata(client, seeded_employees):
    response = client.get("/api/employees")

    assert response.status_code == 200
    body = response.json()
    assert [
        {key: value for key, value in item.items() if key != "updated_at"}
        for item in body["items"]
    ] == [
            {
                "employee_id": "E001",
                "name": "Alice Morgan",
                "country": "US",
                "department": "Engineering",
                "salary_amount": "85000.00",
                "currency": "USD",
            },
            {
                "employee_id": "E002",
                "name": "Alice Morgan",
                "country": "US",
                "department": "Design",
                "salary_amount": "80000.00",
                "currency": "USD",
            },
            {
                "employee_id": "E003",
                "name": "Bob Singh",
                "country": "CA",
                "department": "Engineering",
                "salary_amount": "90000.00",
                "currency": "CAD",
            },
            {
                "employee_id": "E004",
                "name": "Chika Tanaka",
                "country": "JP",
                "department": "Engineering",
                "salary_amount": "7000000",
                "currency": "JPY",
            },
            {
                "employee_id": "E005",
                "name": "Dana Lewis",
                "country": "CA",
                "department": "HR",
                "salary_amount": "75000.00",
                "currency": "CAD",
            },
    ]
    assert body["total"] == 5
    assert body["page"] == 1
    assert body["page_size"] == 25


def test_updated_at_has_explicit_utc_offset(client, seeded_employees):
    response = client.get("/api/employees")

    assert response.status_code == 200
    for item in response.json()["items"]:
        timestamp = item["updated_at"]
        assert timestamp.endswith(("Z", "+00:00"))
        parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert parsed_timestamp.utcoffset() == timedelta(0)


def test_unsupported_currency_is_rejected_clearly(client, test_session_factory):
    with test_session_factory() as session:
        session.add(
            Employee(
                employee_id="E999",
                name="Unsupported Currency",
                country="US",
                department="HR",
                salary_minor_units=10000,
                currency="EUR",
            )
        )
        session.commit()

    response = client.get("/api/employees")

    assert response.status_code == 422
    assert response.json() == {"detail": "Unsupported currency code: EUR"}


def test_unsupported_currency_filter_is_rejected(client):
    response = client.get("/api/employees", params={"currency": "EUR"})

    assert response.status_code == 422
    assert response.json() == {"detail": "Unsupported currency code: EUR"}


def test_timezone_aware_updated_at_is_converted_to_utc():
    employee = EmployeeRead(
        employee_id="E001",
        name="Alice Morgan",
        country="US",
        department="Engineering",
        salary_amount="85000.00",
        currency="USD",
        updated_at=datetime(
            2026,
            1,
            1,
            12,
            0,
            tzinfo=timezone(timedelta(hours=5, minutes=30)),
        ),
    )

    assert employee.updated_at.isoformat() == "2026-01-01T06:30:00+00:00"


def test_page_size_is_respected(client, seeded_employees):
    response = client.get("/api/employees", params={"page": 2, "page_size": 2})

    assert response.status_code == 200
    assert [item["employee_id"] for item in response.json()["items"]] == ["E003", "E004"]
    assert response.json()["total"] == 5
    assert response.json()["page"] == 2
    assert response.json()["page_size"] == 2


def test_search_matches_employee_id(client, seeded_employees):
    response = client.get("/api/employees", params={"search": "E003"})

    assert response.status_code == 200
    assert [item["employee_id"] for item in response.json()["items"]] == ["E003"]


def test_search_matches_employee_name_case_insensitively(client, seeded_employees):
    response = client.get("/api/employees", params={"search": "alice"})

    assert response.status_code == 200
    assert [item["employee_id"] for item in response.json()["items"]] == ["E001", "E002"]


def test_country_filter_works(client, seeded_employees):
    response = client.get("/api/employees", params={"country": "CA"})

    assert response.status_code == 200
    assert [item["employee_id"] for item in response.json()["items"]] == ["E003", "E005"]


def test_department_filter_works(client, seeded_employees):
    response = client.get("/api/employees", params={"department": "Engineering"})

    assert response.status_code == 200
    assert [item["employee_id"] for item in response.json()["items"]] == [
        "E001",
        "E003",
        "E004",
    ]


def test_currency_filter_works(client, seeded_employees):
    response = client.get("/api/employees", params={"currency": "CAD"})

    assert response.status_code == 200
    assert [item["employee_id"] for item in response.json()["items"]] == ["E003", "E005"]


def test_default_order_is_employee_id_ascending(client, seeded_employees):
    response = client.get("/api/employees")

    assert response.status_code == 200
    assert [item["employee_id"] for item in response.json()["items"]] == [
        "E001",
        "E002",
        "E003",
        "E004",
        "E005",
    ]


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page": -1},
        {"page_size": 0},
        {"page_size": 101},
    ],
)
def test_invalid_page_or_page_size_is_rejected(client, params, seeded_employees):
    response = client.get("/api/employees", params=params)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "sort_by",
    ["employee_id", "name", "country", "department", "salary", "updated_at"],
)
def test_predefined_sort_fields_are_accepted(client, sort_by, seeded_employees):
    params = {"sort_by": sort_by}
    if sort_by == "salary":
        params["currency"] = "USD"

    response = client.get("/api/employees", params=params)

    assert response.status_code == 200


def test_sorting_uses_employee_id_as_stable_tie_breaker(client, seeded_employees):
    response = client.get(
        "/api/employees",
        params={"sort_by": "name", "sort_order": "asc"},
    )

    assert response.status_code == 200
    assert [item["employee_id"] for item in response.json()["items"][:2]] == ["E001", "E002"]


def test_unknown_sort_field_is_rejected(client, seeded_employees):
    response = client.get("/api/employees", params={"sort_by": "salary_minor_units"})

    assert response.status_code == 422


def test_salary_sort_requires_currency_filter(client, seeded_employees):
    response = client.get("/api/employees", params={"sort_by": "salary"})

    assert response.status_code == 422


def test_salary_sort_is_scoped_to_requested_currency(client, seeded_employees):
    response = client.get(
        "/api/employees",
        params={"sort_by": "salary", "currency": "USD"},
    )

    assert response.status_code == 200
    assert [item["employee_id"] for item in response.json()["items"]] == ["E002", "E001"]