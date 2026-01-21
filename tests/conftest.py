import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database
import models
from main import app


@pytest.fixture(scope="session")
def engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(scope="session")
def SessionLocal(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _db_setup(engine, SessionLocal, monkeypatch):
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(database, "SessionLocal", SessionLocal)
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(SessionLocal):
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[database.get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def user(client):
    response = client.post(
        "/users/",
        json={"name": "Maria Silva", "email": "maria@example.com"},
    )
    return response.json()


@pytest.fixture()
def user_headers(user):
    return {"X-User-Id": str(user["id"])}


@pytest.fixture()
def second_user_id(client, user_headers):
    response = client.post(
        "/users/",
        json={"name": "Joao Souza", "email": "joao@example.com"},
        headers=user_headers,
    )
    return response.json()["id"]


@pytest.fixture()
def meeting_id(client, user_headers, second_user_id):
    response = client.post(
        "/meetings/",
        json={
            "title": "Sprint Planning",
            "description": "Q1 planning",
            "scheduled_time": "2024-01-15T10:00:00Z",
            "attendee_ids": [second_user_id],
        },
        headers=user_headers,
    )
    return response.json()["id"]