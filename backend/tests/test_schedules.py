"""Integration tests for the /api/schedules endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import UserRole
from app.schemas.host import HostCreate
from app.schemas.inventory import InventoryCreate
from app.schemas.user import UserCreate
from app.services.hosts import create_host
from app.services.inventories import create_inventory
from app.services.users import create_user

# ── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
async def admin_user(db_session):
    return await create_user(
        db_session,
        UserCreate(email="admin@sched.com", password="adminpass1", role=UserRole.admin),
        role=UserRole.admin,
    )


@pytest.fixture
async def operator_user(db_session):
    return await create_user(
        db_session,
        UserCreate(email="operator@sched.com", password="operpass1", role=UserRole.operator),
        role=UserRole.operator,
    )


@pytest.fixture
async def viewer_user(db_session):
    return await create_user(
        db_session,
        UserCreate(email="viewer@sched.com", password="viewerpass1", role=UserRole.viewer),
        role=UserRole.viewer,
    )


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post("/api/auth/login", json={"email": email, "password": password})
    return str(resp.json()["access_token"])


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user) -> str:
    return await _login(client, "admin@sched.com", "adminpass1")


@pytest.fixture
async def operator_token(client: AsyncClient, operator_user) -> str:
    return await _login(client, "operator@sched.com", "operpass1")


@pytest.fixture
async def viewer_token(client: AsyncClient, viewer_user) -> str:
    return await _login(client, "viewer@sched.com", "viewerpass1")


@pytest.fixture
async def inventory_id(db_session) -> str:
    host = await create_host(
        db_session,
        HostCreate(name="sched-host", address="10.0.1.1", os_type="linux", connection_type="ssh"),
    )
    inv = await create_inventory(
        db_session,
        InventoryCreate(name="sched-inventory", host_ids=[host.id]),
    )
    return str(inv.id)


CRON = "0 2 * * *"
PLAYBOOK = "playbooks-examples/ping.yml"


def _payload(inventory_id: str, **overrides: object) -> dict:
    base: dict = {
        "name": "nightly-ping",
        "cron_expression": CRON,
        "inventory_id": inventory_id,
        "playbook_path": PLAYBOOK,
        "enabled": True,
    }
    base.update(overrides)
    return base


# ── GET /api/schedules ─────────────────────────────────────────────────────


async def test_list_schedules_empty(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get("/api/schedules", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_schedules_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/schedules")
    assert resp.status_code == 401


async def test_viewer_can_list_schedules(client: AsyncClient, viewer_token: str) -> None:
    resp = await client.get("/api/schedules", headers={"Authorization": f"Bearer {viewer_token}"})
    assert resp.status_code == 200


# ── POST /api/schedules ────────────────────────────────────────────────────


async def test_create_schedule_as_admin(
    client: AsyncClient, admin_token: str, inventory_id: str
) -> None:
    resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "nightly-ping"
    assert body["cron_expression"] == CRON
    assert body["inventory_id"] == inventory_id
    assert body["playbook_path"] == PLAYBOOK
    assert body["enabled"] is True
    assert "id" in body
    assert "created_at" in body


async def test_create_schedule_as_operator(
    client: AsyncClient, operator_token: str, inventory_id: str
) -> None:
    resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id, name="operator-sched"),
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert resp.status_code == 201


async def test_create_schedule_viewer_forbidden(
    client: AsyncClient, viewer_token: str, inventory_id: str
) -> None:
    resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id),
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


async def test_create_schedule_invalid_cron(
    client: AsyncClient, admin_token: str, inventory_id: str
) -> None:
    resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id, cron_expression="bad-cron"),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 422


async def test_create_schedule_missing_inventory(client: AsyncClient, admin_token: str) -> None:
    import uuid

    resp = await client.post(
        "/api/schedules",
        json=_payload(str(uuid.uuid4())),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_create_schedule_duplicate_name(
    client: AsyncClient, admin_token: str, inventory_id: str
) -> None:
    await client.post(
        "/api/schedules",
        json=_payload(inventory_id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code in (409, 422, 500)


# ── GET /api/schedules/{id} ────────────────────────────────────────────────


async def test_get_schedule(client: AsyncClient, admin_token: str, inventory_id: str) -> None:
    create_resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    schedule_id = create_resp.json()["id"]
    resp = await client.get(
        f"/api/schedules/{schedule_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == schedule_id


async def test_get_schedule_not_found(client: AsyncClient, admin_token: str) -> None:
    import uuid

    resp = await client.get(
        f"/api/schedules/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


# ── PATCH /api/schedules/{id} ──────────────────────────────────────────────


async def test_update_schedule(client: AsyncClient, admin_token: str, inventory_id: str) -> None:
    create_resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    schedule_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/schedules/{schedule_id}",
        json={"enabled": False, "cron_expression": "30 6 * * 1"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["enabled"] is False
    assert body["cron_expression"] == "30 6 * * 1"
    assert body["updated_at"] is not None


async def test_update_schedule_viewer_forbidden(
    client: AsyncClient, viewer_token: str, admin_token: str, inventory_id: str
) -> None:
    create_resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    schedule_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/schedules/{schedule_id}",
        json={"enabled": False},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


async def test_update_schedule_not_found(client: AsyncClient, admin_token: str) -> None:
    import uuid

    resp = await client.patch(
        f"/api/schedules/{uuid.uuid4()}",
        json={"enabled": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


# ── DELETE /api/schedules/{id} ─────────────────────────────────────────────


async def test_delete_schedule_as_admin(
    client: AsyncClient, admin_token: str, inventory_id: str
) -> None:
    create_resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    schedule_id = create_resp.json()["id"]
    resp = await client.delete(
        f"/api/schedules/{schedule_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 204
    get_resp = await client.get(
        f"/api/schedules/{schedule_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert get_resp.status_code == 404


async def test_delete_schedule_operator_forbidden(
    client: AsyncClient, operator_token: str, admin_token: str, inventory_id: str
) -> None:
    create_resp = await client.post(
        "/api/schedules",
        json=_payload(inventory_id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    schedule_id = create_resp.json()["id"]
    resp = await client.delete(
        f"/api/schedules/{schedule_id}",
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert resp.status_code == 403


async def test_delete_schedule_not_found(client: AsyncClient, admin_token: str) -> None:
    import uuid

    resp = await client.delete(
        f"/api/schedules/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404
