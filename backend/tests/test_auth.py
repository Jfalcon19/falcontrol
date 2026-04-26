import pytest
from httpx import AsyncClient

from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.services.users import create_user


@pytest.fixture
async def admin_user(db_session):
    return await create_user(
        db_session,
        UserCreate(email="admin@test.com", password="adminpass1", role=UserRole.admin),
        role=UserRole.admin,
    )


@pytest.fixture
async def operator_user(db_session):
    return await create_user(
        db_session,
        UserCreate(email="operator@test.com", password="operatorpass1"),
    )


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user) -> str:
    resp = await client.post(
        "/api/auth/login", json={"email": "admin@test.com", "password": "adminpass1"}
    )
    assert resp.status_code == 200
    return str(resp.json()["access_token"])


# --- Login ---


async def test_login_success(client: AsyncClient, admin_user) -> None:
    resp = await client.post(
        "/api/auth/login", json={"email": "admin@test.com", "password": "adminpass1"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, admin_user) -> None:
    resp = await client.post(
        "/api/auth/login", json={"email": "admin@test.com", "password": "wrongpass"}
    )
    assert resp.status_code == 401


async def test_login_unknown_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/login", json={"email": "nobody@test.com", "password": "somepass1"}
    )
    assert resp.status_code == 401


# --- /me ---


async def test_me_returns_current_user(client: AsyncClient, admin_user, admin_token: str) -> None:
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@test.com"
    assert resp.json()["role"] == "admin"


async def test_me_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


# --- Refresh ---


async def test_refresh_returns_new_tokens(client: AsyncClient, admin_user) -> None:
    login = await client.post(
        "/api/auth/login", json={"email": "admin@test.com", "password": "adminpass1"}
    )
    refresh_token = login.json()["refresh_token"]
    resp = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_refresh_rejects_access_token(
    client: AsyncClient, admin_user, admin_token: str
) -> None:
    resp = await client.post("/api/auth/refresh", json={"refresh_token": admin_token})
    assert resp.status_code == 401


# --- User creation (admin only) ---


async def test_admin_can_create_user(client: AsyncClient, admin_user, admin_token: str) -> None:
    resp = await client.post(
        "/api/users",
        json={"email": "newuser@test.com", "password": "newpass123"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "newuser@test.com"


async def test_operator_cannot_create_user(client: AsyncClient, operator_user) -> None:
    login = await client.post(
        "/api/auth/login", json={"email": "operator@test.com", "password": "operatorpass1"}
    )
    token = login.json()["access_token"]
    resp = await client.post(
        "/api/users",
        json={"email": "another@test.com", "password": "anotherpass1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


async def test_duplicate_email_returns_conflict(
    client: AsyncClient, admin_user, admin_token: str
) -> None:
    resp = await client.post(
        "/api/users",
        json={"email": "admin@test.com", "password": "somepass123"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 409
