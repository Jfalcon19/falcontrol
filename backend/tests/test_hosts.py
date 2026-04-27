import pytest
from httpx import AsyncClient

from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.services.users import create_user

HOST_PAYLOAD = {
    "name": "web-01",
    "address": "192.168.1.10",
    "os_type": "linux",
    "connection_type": "ssh",
    "port": 22,
    "tags": ["production", "web"],
}


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
        UserCreate(email="operator@test.com", password="operatorpass1", role=UserRole.operator),
        role=UserRole.operator,
    )


@pytest.fixture
async def viewer_user(db_session):
    return await create_user(
        db_session,
        UserCreate(email="viewer@test.com", password="viewerpass1", role=UserRole.viewer),
        role=UserRole.viewer,
    )


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post("/api/auth/login", json={"email": email, "password": password})
    return str(resp.json()["access_token"])


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user) -> str:
    return await _login(client, "admin@test.com", "adminpass1")


@pytest.fixture
async def operator_token(client: AsyncClient, operator_user) -> str:
    return await _login(client, "operator@test.com", "operatorpass1")


@pytest.fixture
async def viewer_token(client: AsyncClient, viewer_user) -> str:
    return await _login(client, "viewer@test.com", "viewerpass1")


# --- GET /api/hosts ---


async def test_list_hosts_empty(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get("/api/hosts", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_hosts_returns_created(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/hosts",
        json=HOST_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get("/api/hosts", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "web-01"


async def test_list_hosts_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/hosts")
    assert resp.status_code == 401


async def test_list_hosts_active_only_filter(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    payload2 = {**HOST_PAYLOAD, "name": "web-02", "address": "192.168.1.11"}
    created = await client.post(
        "/api/hosts", json=payload2, headers={"Authorization": f"Bearer {admin_token}"}
    )
    host_id = created.json()["id"]
    await client.patch(
        f"/api/hosts/{host_id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get(
        "/api/hosts?active_only=true", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    names = [h["name"] for h in resp.json()]
    assert "web-01" in names
    assert "web-02" not in names


# --- POST /api/hosts ---


async def test_create_host_as_admin(client: AsyncClient, admin_token: str) -> None:
    resp = await client.post(
        "/api/hosts",
        json=HOST_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "web-01"
    assert body["os_type"] == "linux"
    assert body["connection_type"] == "ssh"
    assert body["port"] == 22
    assert body["tags"] == ["production", "web"]
    assert body["is_active"] is True
    assert "id" in body
    assert "created_at" in body


async def test_create_host_as_operator(client: AsyncClient, operator_token: str) -> None:
    resp = await client.post(
        "/api/hosts",
        json=HOST_PAYLOAD,
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert resp.status_code == 201


async def test_create_host_as_viewer_forbidden(client: AsyncClient, viewer_token: str) -> None:
    resp = await client.post(
        "/api/hosts",
        json=HOST_PAYLOAD,
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


async def test_create_host_duplicate_name(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    resp = await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 409


async def test_create_host_without_auth(client: AsyncClient) -> None:
    resp = await client.post("/api/hosts", json=HOST_PAYLOAD)
    assert resp.status_code == 401


async def test_create_host_invalid_port(client: AsyncClient, admin_token: str) -> None:
    payload = {**HOST_PAYLOAD, "port": 99999}
    resp = await client.post(
        "/api/hosts", json=payload, headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 422


async def test_create_host_too_many_tags(client: AsyncClient, admin_token: str) -> None:
    payload = {**HOST_PAYLOAD, "tags": [f"tag{i}" for i in range(21)]}
    resp = await client.post(
        "/api/hosts", json=payload, headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 422


async def test_create_host_windows_winrm(client: AsyncClient, admin_token: str) -> None:
    payload = {
        "name": "win-srv-01",
        "address": "192.168.1.50",
        "os_type": "windows",
        "connection_type": "winrm",
        "port": 5985,
    }
    resp = await client.post(
        "/api/hosts", json=payload, headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 201
    assert resp.json()["connection_type"] == "winrm"


async def test_create_host_optional_fields_default(client: AsyncClient, admin_token: str) -> None:
    payload = {
        "name": "minimal-host",
        "address": "10.0.0.1",
        "os_type": "linux",
        "connection_type": "ssh",
    }
    resp = await client.post(
        "/api/hosts", json=payload, headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["port"] is None
    assert body["tags"] == []
    assert body["description"] is None


# --- GET /api/hosts/{id} ---


async def test_get_host_by_id(client: AsyncClient, admin_token: str) -> None:
    created = await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    host_id = created.json()["id"]
    resp = await client.get(
        f"/api/hosts/{host_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == host_id


async def test_get_host_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get(
        "/api/hosts/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_get_host_viewer_can_read(
    client: AsyncClient, admin_token: str, viewer_token: str
) -> None:
    created = await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    host_id = created.json()["id"]
    resp = await client.get(
        f"/api/hosts/{host_id}", headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert resp.status_code == 200


# --- PATCH /api/hosts/{id} ---


async def test_patch_host_name_and_tags(client: AsyncClient, admin_token: str) -> None:
    created = await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    host_id = created.json()["id"]
    resp = await client.patch(
        f"/api/hosts/{host_id}",
        json={"name": "web-01-renamed", "tags": ["staging"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "web-01-renamed"
    assert body["tags"] == ["staging"]
    assert body["address"] == "192.168.1.10"


async def test_patch_host_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.patch(
        "/api/hosts/00000000-0000-0000-0000-000000000000",
        json={"name": "ghost"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_patch_host_duplicate_name(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    p2 = {**HOST_PAYLOAD, "name": "web-02", "address": "192.168.1.11"}
    created2 = await client.post(
        "/api/hosts", json=p2, headers={"Authorization": f"Bearer {admin_token}"}
    )
    host2_id = created2.json()["id"]
    resp = await client.patch(
        f"/api/hosts/{host2_id}",
        json={"name": "web-01"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 409


async def test_patch_host_viewer_forbidden(
    client: AsyncClient, admin_token: str, viewer_token: str
) -> None:
    created = await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    host_id = created.json()["id"]
    resp = await client.patch(
        f"/api/hosts/{host_id}",
        json={"name": "hacked"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


# --- DELETE /api/hosts/{id} ---


async def test_delete_host_as_admin(client: AsyncClient, admin_token: str) -> None:
    created = await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    host_id = created.json()["id"]
    resp = await client.delete(
        f"/api/hosts/{host_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 204
    get_resp = await client.get(
        f"/api/hosts/{host_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_resp.status_code == 404


async def test_delete_host_as_operator_forbidden(
    client: AsyncClient, admin_token: str, operator_token: str
) -> None:
    created = await client.post(
        "/api/hosts", json=HOST_PAYLOAD, headers={"Authorization": f"Bearer {admin_token}"}
    )
    host_id = created.json()["id"]
    resp = await client.delete(
        f"/api/hosts/{host_id}", headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert resp.status_code == 403


async def test_delete_host_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.delete(
        "/api/hosts/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404
