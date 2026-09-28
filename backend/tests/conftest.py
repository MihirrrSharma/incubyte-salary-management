import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.db.models import Base, Employee
from app.main import app


@pytest.fixture
def test_session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield session_factory
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(test_session_factory):
    test_client = TestClient(app)
    yield test_client
    test_client.close()


@pytest.fixture
def seeded_employees(test_session_factory):
    employees = [
        Employee(
            employee_id="E003",
            name="Bob Singh",
            country="CA",
            department="Engineering",
            salary_minor_units=9000000,
            currency="CAD",
        ),
        Employee(
            employee_id="E002",
            name="Alice Morgan",
            country="US",
            department="Design",
            salary_minor_units=8000000,
            currency="USD",
        ),
        Employee(
            employee_id="E004",
            name="Chika Tanaka",
            country="JP",
            department="Engineering",
            salary_minor_units=7000000,
            currency="JPY",
        ),
        Employee(
            employee_id="E001",
            name="Alice Morgan",
            country="US",
            department="Engineering",
            salary_minor_units=8500000,
            currency="USD",
        ),
        Employee(
            employee_id="E005",
            name="Dana Lewis",
            country="CA",
            department="HR",
            salary_minor_units=7500000,
            currency="CAD",
        ),
    ]
    with test_session_factory() as session:
        session.add_all(employees)
        session.commit()
    return employees