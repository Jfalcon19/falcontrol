"""Integration tests for GET /api/dashboard."""

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.models.user import UserRole
from app.schemas.host import HostCreate
from app.schemas.inventory import InventoryCreate
from app.schemas.job import JobCreate
from app.schemas.user import UserCreate
from app.services.hosts import create_host
from app.services.inventories import create_inventory
from app.services.jobs import create_job
from app.services.users import create_user

# ── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
async def admin_user(db_session):
    return await create_user(
        db_session,
        UserCreate(email="admin@dash.com", password="adminpass1", role=UserRole.admin),
        role=UserRole.admin,
    )


@pytest.fixture
async def viewer_user(db_session):
    return await create_user(
        db_session,
        UserCreate(email="viewer@dash.com", password="viewerpass1", role=UserRole.viewer),
        role=UserRole.viewer,
    )


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post("/api/auth/login", json={"email": email, "password": password})
    return str(resp.json()["access_token"])


@pytest.fixture
async def admin_token(client: AsyncClient, admin_user) -> str:
    return await _login(client, "admin@dash.com", "adminpass1")


@pytest.fixture
async def viewer_token(client: AsyncClient, viewer_user) -> str:
    return await _login(client, "viewer@dash.com", "viewerpass1")


# ── Tests ──────────────────────────────────────────────────────────────────


async def test_dashboard_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/dashboard")
    assert resp.status_code == 401


async def test_dashboard_empty_db(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get("/api/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_hosts"] == 0
    assert body["total_inventories"] == 0
    assert body["total_schedules"] == 0
    assert body["total_jobs"] == 0
    assert body["running_jobs"] == 0
    assert body["failed_last_24h"] == 0
    assert body["recent_jobs"] == []


async def test_dashboard_viewer_can_access(client: AsyncClient, viewer_token: str) -> None:
    resp = await client.get("/api/dashboard", headers={"Authorization": f"Bearer {viewer_token}"})
    assert resp.status_code == 200


async def test_dashboard_counts_resources(
    client: AsyncClient, admin_token: str, db_session
) -> None:
    host = await create_host(
        db_session,
        HostCreate(name="dash-host", address="10.0.2.1", os_type="linux", connection_type="ssh"),
    )
    inv = await create_inventory(
        db_session,
        InventoryCreate(name="dash-inventory", host_ids=[host.id]),
    )
    with patch("app.tasks.jobs.run_playbook.delay"):
        await create_job(db_session, JobCreate(inventory_id=inv.id, playbook_path="ping.yml"))
        await create_job(db_session, JobCreate(inventory_id=inv.id, playbook_path="ping.yml"))

    resp = await client.get("/api/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_hosts"] == 1
    assert body["total_inventories"] == 1
    assert body["total_jobs"] == 2
    assert len(body["recent_jobs"]) == 2
    # recent_jobs must be ordered newest first
    assert body["recent_jobs"][0]["created_at"] >= body["recent_jobs"][1]["created_at"]
