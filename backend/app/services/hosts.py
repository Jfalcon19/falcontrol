import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.host import Host
from app.schemas.host import HostCreate, HostUpdate


async def get_host_by_id(db: AsyncSession, host_id: uuid.UUID) -> Host | None:
    result = await db.execute(select(Host).where(Host.id == host_id))
    return result.scalar_one_or_none()


async def get_host_by_name(db: AsyncSession, name: str) -> Host | None:
    result = await db.execute(select(Host).where(Host.name == name))
    return result.scalar_one_or_none()


async def list_hosts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
) -> list[Host]:
    query = select(Host)
    if active_only:
        query = query.where(Host.is_active.is_(True))
    query = query.order_by(Host.name).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_host(db: AsyncSession, data: HostCreate) -> Host:
    host = Host(**data.model_dump())
    db.add(host)
    await db.commit()
    await db.refresh(host)
    return host


async def update_host(db: AsyncSession, host: Host, data: HostUpdate) -> Host:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(host, field, value)
    await db.commit()
    await db.refresh(host)
    return host


async def delete_host(db: AsyncSession, host: Host) -> None:
    await db.delete(host)
    await db.commit()
