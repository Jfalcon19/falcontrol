import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, require_operator_or_admin
from app.core.database import get_db
from app.models.inventory import Inventory
from app.models.user import User
from app.schemas.inventory import InventoryCreate, InventoryRead, InventoryUpdate
from app.services.inventories import (
    create_inventory,
    delete_inventory,
    get_inventory_by_id,
    get_inventory_by_name,
    list_inventories,
    update_inventory,
)

router = APIRouter(prefix="/inventories", tags=["inventories"])


@router.get("", response_model=list[InventoryRead])
async def get_inventories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[Inventory]:
    return await list_inventories(db, skip=skip, limit=limit)


@router.post("", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
async def create_new_inventory(
    body: InventoryCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator_or_admin),
) -> Inventory:
    existing = await get_inventory_by_name(db, body.name)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Inventory name already exists"
        )
    return await create_inventory(db, body)


@router.get("/{inventory_id}", response_model=InventoryRead)
async def get_inventory(
    inventory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> Inventory:
    inventory = await get_inventory_by_id(db, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return inventory


@router.patch("/{inventory_id}", response_model=InventoryRead)
async def update_existing_inventory(
    inventory_id: uuid.UUID,
    body: InventoryUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_operator_or_admin),
) -> Inventory:
    inventory = await get_inventory_by_id(db, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    if body.name is not None and body.name != inventory.name:
        conflict = await get_inventory_by_name(db, body.name)
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Inventory name already exists"
            )
    return await update_inventory(db, inventory, body)


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_inventory(
    inventory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> None:
    inventory = await get_inventory_by_id(db, inventory_id)
    if inventory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    await delete_inventory(db, inventory)
