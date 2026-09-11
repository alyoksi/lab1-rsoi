from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

# in-memory SQLite
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_create_person():
    response = client.post("/api/v1/persons", json={"name": "Ivan", "age": 21})
    assert response.status_code == 201
    assert response.headers["location"].startswith("/api/v1/persons/")


def test_get_person():
    create = client.post("/api/v1/persons", json={"name": "Petr", "age": 30})
    person_id = create.headers["location"].split("/")[-1]

    response = client.get(f"/api/v1/persons/{person_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Petr"


def test_get_person_not_found():
    response = client.get("/api/v1/persons/999999")
    assert response.status_code == 404


def test_list_persons():
    response = client.get("/api/v1/persons")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_person():
    create = client.post("/api/v1/persons", json={"name": "Anna", "age": 25})
    person_id = create.headers["location"].split("/")[-1]

    response = client.patch(f"/api/v1/persons/{person_id}", json={"name": "Anna", "age": 26})
    assert response.status_code == 200
    assert response.json()["age"] == 26


def test_update_person_preserves_unset_fields():
    create = client.post(
        "/api/v1/persons",
        json={"name": "Sergey", "age": 33, "address": "Old street", "work": "Bauman"},
    )
    person_id = create.headers["location"].split("/")[-1]

    # PATCH передаёт только name и address — age и work трогать не должен
    response = client.patch(
        f"/api/v1/persons/{person_id}",
        json={"name": "Sergey Updated", "address": "New street"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Sergey Updated"
    assert body["address"] == "New street"
    assert body["age"] == 33
    assert body["work"] == "Bauman"


def test_delete_person():
    create = client.post("/api/v1/persons", json={"name": "Oleg", "age": 40})
    person_id = create.headers["location"].split("/")[-1]

    response = client.delete(f"/api/v1/persons/{person_id}")
    assert response.status_code == 204

    response = client.get(f"/api/v1/persons/{person_id}")
    assert response.status_code == 404
