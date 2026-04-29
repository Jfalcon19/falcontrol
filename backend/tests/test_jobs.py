from unittest.mock import patch

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
async def inventory_id(db_session) -> str:
    host = await create_host(
        db_session,
        HostCreate(name="web-01", address="10.0.0.1", os_type="linux", connection_type="ssh"),
    )
    inv = await create_inventory(
        db_session,
        InventoryCreate(name="test-inventory", host_ids=[host.id]),
    )
    return str(inv.id)


JOB_PLAYBOOK = "playbooks-examples/ping.yml"


def _patch_celery():
    return patch("app.api.jobs.run_playbook.delay")


# ── GET /api/jobs ──────────────────────────────────────────────────────────


async def test_list_jobs_empty(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get("/api/jobs", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_jobs_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/jobs")
    assert resp.status_code == 401


# ── POST /api/jobs ─────────────────────────────────────────────────────────


async def test_create_job_as_admin(
    client: AsyncClient, admin_token: str, inventory_id: str
) -> None:
    with _patch_celery() as mock_delay:
        resp = await client.post(
            "/api/jobs",
            json={"inventory_id": inventory_id, "playbook_path": JOB_PLAYBOOK},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["inventory_id"] == inventory_id
    assert body["playbook_path"] == JOB_PLAYBOOK
    assert "stdout" not in body
    assert "id" in body
    mock_delay.assert_called_once_with(body["id"])


async def test_create_job_as_operator(
    client: AsyncClient, operator_token: str, inventory_id: str
) -> None:
    with _patch_celery():
        resp = await client.post(
            "/api/jobs",
            json={"inventory_id": inventory_id, "playbook_path": JOB_PLAYBOOK},
            headers={"Authorization": f"Bearer {operator_token}"},
        )
    assert resp.status_code == 201


async def test_create_job_viewer_forbidden(
    client: AsyncClient, viewer_token: str, inventory_id: str
) -> None:
    resp = await client.post(
        "/api/jobs",
        json={"inventory_id": inventory_id, "playbook_path": JOB_PLAYBOOK},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


async def test_create_job_without_auth(client: AsyncClient, inventory_id: str) -> None:
    resp = await client.post(
        "/api/jobs",
        json={"inventory_id": inventory_id, "playbook_path": JOB_PLAYBOOK},
    )
    assert resp.status_code == 401


async def test_create_job_invalid_inventory(client: AsyncClient, admin_token: str) -> None:
    with _patch_celery():
        resp = await client.post(
            "/api/jobs",
            json={
                "inventory_id": "00000000-0000-0000-0000-000000000000",
                "playbook_path": JOB_PLAYBOOK,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    assert resp.status_code == 404


# ── GET /api/jobs/{id} ─────────────────────────────────────────────────────


async def test_get_job_by_id(client: AsyncClient, admin_token: str, inventory_id: str) -> None:
    with _patch_celery():
        created = await client.post(
            "/api/jobs",
            json={"inventory_id": inventory_id, "playbook_path": JOB_PLAYBOOK},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    job_id = created.json()["id"]
    resp = await client.get(
        f"/api/jobs/{job_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == job_id
    assert "stdout" in body


async def test_get_job_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get(
        "/api/jobs/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_get_job_viewer_can_read(
    client: AsyncClient, admin_token: str, viewer_token: str, inventory_id: str
) -> None:
    with _patch_celery():
        created = await client.post(
            "/api/jobs",
            json={"inventory_id": inventory_id, "playbook_path": JOB_PLAYBOOK},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    job_id = created.json()["id"]
    resp = await client.get(
        f"/api/jobs/{job_id}", headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert resp.status_code == 200


# ── DELETE /api/jobs/{id} ──────────────────────────────────────────────────


async def test_delete_job_as_admin(
    client: AsyncClient, admin_token: str, inventory_id: str
) -> None:
    with _patch_celery():
        created = await client.post(
            "/api/jobs",
            json={"inventory_id": inventory_id, "playbook_path": JOB_PLAYBOOK},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    job_id = created.json()["id"]
    resp = await client.delete(
        f"/api/jobs/{job_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 204
    get_resp = await client.get(
        f"/api/jobs/{job_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_resp.status_code == 404


async def test_delete_job_operator_forbidden(
    client: AsyncClient, admin_token: str, operator_token: str, inventory_id: str
) -> None:
    with _patch_celery():
        created = await client.post(
            "/api/jobs",
            json={"inventory_id": inventory_id, "playbook_path": JOB_PLAYBOOK},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    job_id = created.json()["id"]
    resp = await client.delete(
        f"/api/jobs/{job_id}", headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert resp.status_code == 403


async def test_delete_job_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.delete(
        "/api/jobs/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


# ── Lista refleja jobs creados ─────────────────────────────────────────────


async def test_list_jobs_returns_created(
    client: AsyncClient, admin_token: str, inventory_id: str
) -> None:
    with _patch_celery():
        await client.post(
            "/api/jobs",
            json={"inventory_id": inventory_id, "playbook_path": JOB_PLAYBOOK},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        await client.post(
            "/api/jobs",
            json={"inventory_id": inventory_id, "playbook_path": "other.yml"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    resp = await client.get("/api/jobs", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 2
