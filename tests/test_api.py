import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Make project root importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from main import app
from database import Base, get_db
from models import User, Task as TaskModel
from security import hash_password



# Test database setup

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)



# Pytest fixtures

@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def create_user(email: str, password: str, role: str = "user"):
    db = TestingSessionLocal()
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user



# Auth tests

def test_register_success():
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "mypassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "user"
    assert "id" in data


def test_register_duplicate_email():
    create_user("duplicate@example.com", "password123")

    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "anotherpassword",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_login_success():
    create_user("login@example.com", "password123")

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure_wrong_password():
    create_user("wrongpass@example.com", "correctpassword")

    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "badpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_requires_auth():
    response = client.get("/me")
    assert response.status_code in (401, 403)


def test_me_with_valid_token():
    create_user("me@example.com", "password123")

    login_response = client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["role"] == "user"
    assert "id" in data

def get_auth_headers(email: str, password: str):
    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_creates_task_with_own_owner_id():
    user = create_user("taskowner@example.com", "password123")

    headers = get_auth_headers("taskowner@example.com", "password123")

    response = client.post(
        "/tasks",
        json={"title": "My Task"},
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Task"
    assert data["completed"] is False
    assert data["owner_id"] == user.id


def test_user_sees_only_their_own_tasks():
    user1 = create_user("user1@example.com", "password123")
    user2 = create_user("user2@example.com", "password123")

    db = TestingSessionLocal()
    db.add_all([
        TaskModel(title="User1 Task", completed=False, owner_id=user1.id),
        TaskModel(title="User2 Task", completed=False, owner_id=user2.id),
    ])
    db.commit()
    db.close()

    headers = get_auth_headers("user1@example.com", "password123")

    response = client.get("/tasks", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "User1 Task"
    assert data[0]["owner_id"] == user1.id


def test_admin_sees_all_tasks():
    admin = create_user("admin@example.com", "password123", role="admin")
    user = create_user("normal@example.com", "password123", role="user")

    db = TestingSessionLocal()
    db.add_all([
        TaskModel(title="Admin Task", completed=False, owner_id=admin.id),
        TaskModel(title="User Task", completed=False, owner_id=user.id),
    ])
    db.commit()
    db.close()

    headers = get_auth_headers("admin@example.com", "password123")

    response = client.get("/tasks", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_user_cannot_access_another_users_task():
    user1 = create_user("owner@example.com", "password123")
    user2 = create_user("intruder@example.com", "password123")

    db = TestingSessionLocal()
    task = TaskModel(title="Private Task", completed=False, owner_id=user1.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()

    headers = get_auth_headers("intruder@example.com", "password123")

    response = client.get(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to access this task"


def test_user_can_patch_own_task():
    user = create_user("patchuser@example.com", "password123")

    db = TestingSessionLocal()
    task = TaskModel(title="Old Title", completed=False, owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()

    headers = get_auth_headers("patchuser@example.com", "password123")

    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "New Title", "completed": True},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["completed"] is True
    assert data["owner_id"] == user.id


def test_admin_can_delete_any_task():
    admin = create_user("deleteadmin@example.com", "password123", role="admin")
    user = create_user("deleteuser@example.com", "password123", role="user")

    db = TestingSessionLocal()
    task = TaskModel(title="Delete Me", completed=False, owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()

    headers = get_auth_headers("deleteadmin@example.com", "password123")

    response = client.delete(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted"
