from datetime import datetime, timezone

from app.db.models import Employee


def test_successful_salary_update_persists_exact_minor_units_and_utc_timestamp(
    client,
    test_session_factory,
    seeded_employees,
):
    previous_timestamp = datetime(2000, 1, 1, tzinfo=timezone.utc)
    with test_session_factory() as session:
        employee = session.get(Employee, "E001")
        employee.updated_at = previous_timestamp
        session.commit()

    response = client.patch(
        "/api/employees/E001/salary",
        json={"salary_amount": "1234.56"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == "E001"
    assert body["salary_amount"] == "1234.56"
    assert body["currency"] == "USD"
    assert body["updated_at"].endswith(("Z", "+00:00"))
    updated_timestamp = datetime.fromisoformat(
        body["updated_at"].replace("Z", "+00:00")
    )
    assert updated_timestamp.utcoffset().total_seconds() == 0
    assert updated_timestamp > previous_timestamp

    with test_session_factory() as session:
        stored_employee = session.get(Employee, "E001")
        assert stored_employee.salary_minor_units == 123456
        assert stored_employee.currency == "USD"
        assert stored_employee.updated_at.replace(tzinfo=timezone.utc) == updated_timestamp


def test_zero_salary_is_valid(client, test_session_factory, seeded_employees):
    response = client.patch(
        "/api/employees/E001/salary",
        json={"salary_amount": "0.00"},
    )

    assert response.status_code == 200
    assert response.json()["salary_amount"] == "0.00"
    with test_session_factory() as session:
        assert session.get(Employee, "E001").salary_minor_units == 0


def test_negative_salary_is_rejected(client, seeded_employees):
    response = client.patch(
        "/api/employees/E001/salary",
        json={"salary_amount": "-1.00"},
    )

    assert response.status_code == 422


def test_malformed_salary_is_rejected(client, seeded_employees):
    response = client.patch(
        "/api/employees/E001/salary",
        json={"salary_amount": "not-a-decimal"},
    )

    assert response.status_code == 422


def test_salary_must_be_a_decimal_string(client, seeded_employees):
    response = client.patch(
        "/api/employees/E001/salary",
        json={"salary_amount": 85000},
    )

    assert response.status_code == 422


def test_excessive_currency_precision_is_rejected(client, seeded_employees):
    response = client.patch(
        "/api/employees/E001/salary",
        json={"salary_amount": "85000.001"},
    )

    assert response.status_code == 422


def test_unknown_employee_returns_not_found(client):
    response = client.patch(
        "/api/employees/MISSING/salary",
        json={"salary_amount": "85000.00"},
    )

    assert response.status_code == 404


def test_request_cannot_change_employee_currency(client, seeded_employees):
    response = client.patch(
        "/api/employees/E001/salary",
        json={"salary_amount": "85000.00", "currency": "EUR"},
    )

    assert response.status_code == 422


def test_salary_outside_sqlite_integer_range_is_rejected(client, seeded_employees):
    response = client.patch(
        "/api/employees/E001/salary",
        json={"salary_amount": "92233720368547758.08"},
    )

    assert response.status_code == 422