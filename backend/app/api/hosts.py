import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, require_operator_or_admin
from app.core.database import get_db
from app.models.host import Host
from app.models.user import User
from app.schemas.host import HostCreate, HostRead, HostUpdate
from app.services.hosts import (
    create_host,
    delete_host,
    get_host_by_id,
    get_host_by_name,
    list_hosts,
    update_host,
)

router = APIRouter(prefix="/hosts", tags=["hosts"])


@router.get("", response_model=list[HostRead])
async def get_hosts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    active_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[Host]:
    return await list_hosts(db, skip=skip, limit=limit, active_only=active_only)


@router.post("", response_model=HostRead, status_code=status.HTTP_201_CREATED)
async def create_new_host(
    body: HostCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator_or_admin),
) -> Host:
    existing = await get_host_by_name(db, body.name)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Host name already exists")
    return await create_host(db, body)


@router.get("/{host_id}", response_model=HostRead)
async def get_host(
    host_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> Host:
    host = await get_host_by_id(db, host_id)
    if host is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    return host


@router.patch("/{host_id}", response_model=HostRead)
async def update_existing_host(
    host_id: uuid.UUID,
    body: HostUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator_or_admin),
) -> Host:
    host = await get_host_by_id(db, host_id)
    if host is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    if body.name is not None and body.name != host.name:
        conflict = await get_host_by_name(db, body.name)
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Host name already exists"
            )
    return await update_host(db, host, body)


@router.delete("/{host_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_host(
    host_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> None:
    host = await get_host_by_id(db, host_id)
    if host is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    await delete_host(db, host)
