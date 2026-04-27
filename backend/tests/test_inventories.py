import pytest
from httpx import AsyncClient

from app.models.user import UserRole
from app.schemas.host import HostCreate
from app.schemas.user import UserCreate
from app.services.hosts import create_host
from app.services.users import create_user

INVENTORY_PAYLOAD = {"name": "prod-servers", "description": "Servidores de producción"}

HOST_DATA = {
    "name": "web-01",
    "address": "192.168.1.10",
    "os_type": "linux",
    "connection_type": "ssh",
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


@pytest.fixture
async def host_id(db_session) -> str:
    host = await create_host(db_session, HostCreate(**HOST_DATA))
    return str(host.id)


# --- GET /api/inventories ---


async def test_list_inventories_empty(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get("/api/inventories", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_inventories_returns_created(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get("/api/inventories", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "prod-servers"


async def test_list_inventories_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/inventories")
    assert resp.status_code == 401


# --- POST /api/inventories ---


async def test_create_inventory_as_admin(client: AsyncClient, admin_token: str) -> None:
    resp = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "prod-servers"
    assert body["description"] == "Servidores de producción"
    assert body["hosts"] == []
    assert "id" in body
    assert "created_at" in body


async def test_create_inventory_as_operator(client: AsyncClient, operator_token: str) -> None:
    resp = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert resp.status_code == 201


async def test_create_inventory_as_viewer_forbidden(client: AsyncClient, viewer_token: str) -> None:
    resp = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


async def test_create_inventory_duplicate_name(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 409


async def test_create_inventory_without_auth(client: AsyncClient) -> None:
    resp = await client.post("/api/inventories", json=INVENTORY_PAYLOAD)
    assert resp.status_code == 401


async def test_create_inventory_with_hosts(
    client: AsyncClient, admin_token: str, host_id: str
) -> None:
    payload = {**INVENTORY_PAYLOAD, "host_ids": [host_id]}
    resp = await client.post(
        "/api/inventories",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["hosts"]) == 1
    assert body["hosts"][0]["id"] == host_id


async def test_create_inventory_ignores_unknown_host_ids(
    client: AsyncClient, admin_token: str
) -> None:
    payload = {**INVENTORY_PAYLOAD, "host_ids": ["00000000-0000-0000-0000-000000000000"]}
    resp = await client.post(
        "/api/inventories",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["hosts"] == []


# --- GET /api/inventories/{id} ---


async def test_get_inventory_by_id(client: AsyncClient, admin_token: str) -> None:
    created = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv_id = created.json()["id"]
    resp = await client.get(
        f"/api/inventories/{inv_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == inv_id


async def test_get_inventory_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get(
        "/api/inventories/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_get_inventory_viewer_can_read(
    client: AsyncClient, admin_token: str, viewer_token: str
) -> None:
    created = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv_id = created.json()["id"]
    resp = await client.get(
        f"/api/inventories/{inv_id}", headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert resp.status_code == 200


# --- PATCH /api/inventories/{id} ---


async def test_patch_inventory_name(client: AsyncClient, admin_token: str) -> None:
    created = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv_id = created.json()["id"]
    resp = await client.patch(
        f"/api/inventories/{inv_id}",
        json={"name": "staging-servers"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "staging-servers"
    assert resp.json()["description"] == "Servidores de producción"


async def test_patch_inventory_replace_hosts(
    client: AsyncClient, admin_token: str, host_id: str
) -> None:
    created = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv_id = created.json()["id"]
    resp = await client.patch(
        f"/api/inventories/{inv_id}",
        json={"host_ids": [host_id]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert len(resp.json()["hosts"]) == 1
    resp2 = await client.patch(
        f"/api/inventories/{inv_id}",
        json={"host_ids": []},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["hosts"] == []


async def test_patch_inventory_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.patch(
        "/api/inventories/00000000-0000-0000-0000-000000000000",
        json={"name": "ghost"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_patch_inventory_duplicate_name(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv2 = await client.post(
        "/api/inventories",
        json={"name": "staging-servers"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv2_id = inv2.json()["id"]
    resp = await client.patch(
        f"/api/inventories/{inv2_id}",
        json={"name": "prod-servers"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 409


async def test_patch_inventory_viewer_forbidden(
    client: AsyncClient, admin_token: str, viewer_token: str
) -> None:
    created = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv_id = created.json()["id"]
    resp = await client.patch(
        f"/api/inventories/{inv_id}",
        json={"name": "hacked"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


# --- DELETE /api/inventories/{id} ---


async def test_delete_inventory_as_admin(client: AsyncClient, admin_token: str) -> None:
    created = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv_id = created.json()["id"]
    resp = await client.delete(
        f"/api/inventories/{inv_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 204
    get_resp = await client.get(
        f"/api/inventories/{inv_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_resp.status_code == 404


async def test_delete_inventory_as_operator_forbidden(
    client: AsyncClient, admin_token: str, operator_token: str
) -> None:
    created = await client.post(
        "/api/inventories",
        json=INVENTORY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv_id = created.json()["id"]
    resp = await client.delete(
        f"/api/inventories/{inv_id}", headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert resp.status_code == 403


async def test_delete_inventory_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.delete(
        "/api/inventories/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_delete_inventory_does_not_delete_hosts(
    client: AsyncClient, admin_token: str, host_id: str
) -> None:
    payload = {**INVENTORY_PAYLOAD, "host_ids": [host_id]}
    created = await client.post(
        "/api/inventories",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    inv_id = created.json()["id"]
    await client.delete(
        f"/api/inventories/{inv_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    host_resp = await client.get(
        f"/api/hosts/{host_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert host_resp.status_code == 200
