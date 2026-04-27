import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, require_operator_or_admin
from app.core.database import get_db
from app.models.credential import Credential
from app.models.user import User
from app.schemas.credential import CredentialCreate, CredentialRead, CredentialUpdate
from app.services.credentials import (
    create_credential,
    delete_credential,
    get_credential_by_id,
    get_credential_by_name,
    list_credentials,
    update_credential,
)

router = APIRouter(prefix="/credentials", tags=["credentials"])


@router.get("", response_model=list[CredentialRead])
async def get_credentials(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[Credential]:
    return await list_credentials(db, skip=skip, limit=limit)


@router.post("", response_model=CredentialRead, status_code=status.HTTP_201_CREATED)
async def create_new_credential(
    body: CredentialCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator_or_admin),
) -> Credential:
    existing = await get_credential_by_name(db, body.name)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Credential name already exists"
        )
    return await create_credential(db, body)


@router.get("/{credential_id}", response_model=CredentialRead)
async def get_credential(
    credential_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> Credential:
    credential = await get_credential_by_id(db, credential_id)
    if credential is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    return credential


@router.patch("/{credential_id}", response_model=CredentialRead)
async def update_existing_credential(
    credential_id: uuid.UUID,
    body: CredentialUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator_or_admin),
) -> Credential:
    credential = await get_credential_by_id(db, credential_id)
    if credential is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    if body.name is not None and body.name != credential.name:
        conflict = await get_credential_by_name(db, body.name)
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Credential name already exists"
            )
    return await update_credential(db, credential, body)


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_credential(
    credential_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> None:
    credential = await get_credential_by_id(db, credential_id)
    if credential is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    await delete_credential(db, credential)
