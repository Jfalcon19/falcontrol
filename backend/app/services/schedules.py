import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate


async def create_schedule(db: AsyncSession, data: ScheduleCreate) -> Schedule:
    inv = await db.get(Inventory, data.inventory_id)
    if inv is None:
        raise ValueError("inventory not found")
    schedule = Schedule(
        name=data.name,
        cron_expression=data.cron_expression,
        inventory_id=data.inventory_id,
        playbook_path=data.playbook_path,
        enabled=data.enabled,
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


async def list_schedules(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Schedule]:
    result = await db.execute(select(Schedule).order_by(Schedule.name).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_schedule_by_id(db: AsyncSession, schedule_id: uuid.UUID) -> Schedule | None:
    return await db.get(Schedule, schedule_id)


async def update_schedule(db: AsyncSession, schedule: Schedule, data: ScheduleUpdate) -> Schedule:
    if data.inventory_id is not None and data.inventory_id != schedule.inventory_id:
        inv = await db.get(Inventory, data.inventory_id)
        if inv is None:
            raise ValueError("inventory not found")

    patch = data.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(schedule, field, value)
    schedule.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(schedule)
    return schedule


async def delete_schedule(db: AsyncSession, schedule: Schedule) -> None:
    await db.delete(schedule)
    await db.commit()
