import pytest
from httpx import AsyncClient

from app.models.user import UserRole
from app.schemas.user import UserCreate
from app.services.users import create_user

SSH_KEY_PAYLOAD = {
    "name": "prod-ssh-key",
    "credential_type": "ssh_key",
    "secret": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAK...",
}

SSH_PASS_PAYLOAD = {
    "name": "prod-ssh-pass",
    "credential_type": "ssh_password",
    "username": "deploy",
    "secret": "s3cur3p@ss",
}

WINRM_PAYLOAD = {
    "name": "win-admin",
    "credential_type": "winrm",
    "username": "Administrator",
    "secret": "W!nRM_pass1",
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


def _no_secrets_leaked(body: dict) -> bool:
    forbidden = {"secret", "encrypted_secret", "encrypted_passphrase", "passphrase"}
    return not forbidden.intersection(body.keys())


# --- GET /api/credentials ---


async def test_list_credentials_empty(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get("/api/credentials", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_credentials_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/credentials")
    assert resp.status_code == 401


async def test_list_credentials_no_secrets(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.get("/api/credentials", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    for item in resp.json():
        assert _no_secrets_leaked(item)


# --- POST /api/credentials ---


async def test_create_ssh_key_credential(client: AsyncClient, admin_token: str) -> None:
    resp = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "prod-ssh-key"
    assert body["credential_type"] == "ssh_key"
    assert body["username"] is None
    assert "id" in body
    assert _no_secrets_leaked(body)


async def test_create_ssh_key_with_passphrase(client: AsyncClient, admin_token: str) -> None:
    payload = {**SSH_KEY_PAYLOAD, "passphrase": "key-passphrase"}
    resp = await client.post(
        "/api/credentials",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    assert _no_secrets_leaked(resp.json())


async def test_create_ssh_password_credential(client: AsyncClient, admin_token: str) -> None:
    resp = await client.post(
        "/api/credentials",
        json=SSH_PASS_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "deploy"
    assert _no_secrets_leaked(body)


async def test_create_winrm_credential(client: AsyncClient, admin_token: str) -> None:
    resp = await client.post(
        "/api/credentials",
        json=WINRM_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["credential_type"] == "winrm"
    assert _no_secrets_leaked(resp.json())


async def test_create_credential_as_operator(client: AsyncClient, operator_token: str) -> None:
    resp = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert resp.status_code == 201


async def test_create_credential_as_viewer_forbidden(
    client: AsyncClient, viewer_token: str
) -> None:
    resp = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


async def test_create_credential_without_auth(client: AsyncClient) -> None:
    resp = await client.post("/api/credentials", json=SSH_KEY_PAYLOAD)
    assert resp.status_code == 401


async def test_create_credential_duplicate_name(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    resp = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 409


async def test_create_ssh_password_without_username_fails(
    client: AsyncClient, admin_token: str
) -> None:
    payload = {"name": "bad-cred", "credential_type": "ssh_password", "secret": "pass123"}
    resp = await client.post(
        "/api/credentials",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 422


async def test_create_winrm_without_username_fails(client: AsyncClient, admin_token: str) -> None:
    payload = {"name": "bad-winrm", "credential_type": "winrm", "secret": "pass123"}
    resp = await client.post(
        "/api/credentials",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 422


async def test_create_ssh_key_without_username_ok(client: AsyncClient, admin_token: str) -> None:
    payload = {
        "name": "keyonly",
        "credential_type": "ssh_key",
        "secret": "-----BEGIN RSA PRIVATE KEY-----\nMIIE...",
    }
    resp = await client.post(
        "/api/credentials",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201


# --- GET /api/credentials/{id} ---


async def test_get_credential_by_id(client: AsyncClient, admin_token: str) -> None:
    created = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    cred_id = created.json()["id"]
    resp = await client.get(
        f"/api/credentials/{cred_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == cred_id
    assert _no_secrets_leaked(resp.json())


async def test_get_credential_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.get(
        "/api/credentials/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_get_credential_viewer_can_read(
    client: AsyncClient, admin_token: str, viewer_token: str
) -> None:
    created = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    cred_id = created.json()["id"]
    resp = await client.get(
        f"/api/credentials/{cred_id}", headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert resp.status_code == 200
    assert _no_secrets_leaked(resp.json())


# --- PATCH /api/credentials/{id} ---


async def test_patch_credential_name(client: AsyncClient, admin_token: str) -> None:
    created = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    cred_id = created.json()["id"]
    resp = await client.patch(
        f"/api/credentials/{cred_id}",
        json={"name": "renamed-key"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "renamed-key"
    assert _no_secrets_leaked(resp.json())


async def test_patch_credential_secret_re_encrypted(
    client: AsyncClient, admin_token: str, db_session
) -> None:
    import uuid as _uuid

    from app.services.credentials import get_credential_by_id
    from app.services.vault import decrypt

    created = await client.post(
        "/api/credentials",
        json=SSH_PASS_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    cred_id = created.json()["id"]
    resp = await client.patch(
        f"/api/credentials/{cred_id}",
        json={"secret": "newpassword123"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert _no_secrets_leaked(resp.json())
    cred = await get_credential_by_id(db_session, _uuid.UUID(cred_id))
    assert cred is not None
    assert decrypt(cred.encrypted_secret) == "newpassword123"


async def test_patch_credential_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.patch(
        "/api/credentials/00000000-0000-0000-0000-000000000000",
        json={"name": "ghost"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_patch_credential_duplicate_name(client: AsyncClient, admin_token: str) -> None:
    await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    c2 = await client.post(
        "/api/credentials",
        json=SSH_PASS_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    cred2_id = c2.json()["id"]
    resp = await client.patch(
        f"/api/credentials/{cred2_id}",
        json={"name": "prod-ssh-key"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 409


async def test_patch_credential_viewer_forbidden(
    client: AsyncClient, admin_token: str, viewer_token: str
) -> None:
    created = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    cred_id = created.json()["id"]
    resp = await client.patch(
        f"/api/credentials/{cred_id}",
        json={"name": "hacked"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403


# --- DELETE /api/credentials/{id} ---


async def test_delete_credential_as_admin(client: AsyncClient, admin_token: str) -> None:
    created = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    cred_id = created.json()["id"]
    resp = await client.delete(
        f"/api/credentials/{cred_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 204
    get_resp = await client.get(
        f"/api/credentials/{cred_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_resp.status_code == 404


async def test_delete_credential_as_operator_forbidden(
    client: AsyncClient, admin_token: str, operator_token: str
) -> None:
    created = await client.post(
        "/api/credentials",
        json=SSH_KEY_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    cred_id = created.json()["id"]
    resp = await client.delete(
        f"/api/credentials/{cred_id}", headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert resp.status_code == 403


async def test_delete_credential_not_found(client: AsyncClient, admin_token: str) -> None:
    resp = await client.delete(
        "/api/credentials/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


# --- Verificación de cifrado en BD ---


async def test_secret_stored_encrypted_in_db(
    client: AsyncClient, admin_token: str, db_session
) -> None:
    import uuid as _uuid

    from app.services.credentials import get_credential_by_id
    from app.services.vault import decrypt

    resp = await client.post(
        "/api/credentials",
        json=SSH_PASS_PAYLOAD,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    cred_id = resp.json()["id"]
    cred = await get_credential_by_id(db_session, _uuid.UUID(cred_id))
    assert cred is not None
    assert cred.encrypted_secret != "s3cur3p@ss"
    assert decrypt(cred.encrypted_secret) == "s3cur3p@ss"
