import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.host import Host
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate


async def _resolve_hosts(db: AsyncSession, host_ids: list[uuid.UUID]) -> list[Host]:
    if not host_ids:
        return []
    result = await db.execute(select(Host).where(Host.id.in_(host_ids)))
    return list(result.scalars().all())


async def get_inventory_by_id(db: AsyncSession, inventory_id: uuid.UUID) -> Inventory | None:
    result = await db.execute(select(Inventory).where(Inventory.id == inventory_id))
    return result.scalar_one_or_none()


async def get_inventory_by_name(db: AsyncSession, name: str) -> Inventory | None:
    result = await db.execute(select(Inventory).where(Inventory.name == name))
    return result.scalar_one_or_none()


async def list_inventories(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Inventory]:
    result = await db.execute(select(Inventory).order_by(Inventory.name).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_inventory(db: AsyncSession, data: InventoryCreate) -> Inventory:
    hosts = await _resolve_hosts(db, data.host_ids)
    inventory = Inventory(name=data.name, description=data.description, hosts=hosts)
    db.add(inventory)
    await db.commit()
    await db.refresh(inventory)
    return inventory


async def update_inventory(
    db: AsyncSession, inventory: Inventory, data: InventoryUpdate
) -> Inventory:
    if data.name is not None:
        inventory.name = data.name
    if data.description is not None:
        inventory.description = data.description
    if data.host_ids is not None:
        inventory.hosts = await _resolve_hosts(db, data.host_ids)
    await db.commit()
    await db.refresh(inventory)
    return inventory


async def delete_inventory(db: AsyncSession, inventory: Inventory) -> None:
    await db.delete(inventory)
    await db.commit()
