import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, require_operator_or_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleRead, ScheduleUpdate
from app.services.schedules import (
    create_schedule,
    delete_schedule,
    get_schedule_by_id,
    list_schedules,
    update_schedule,
)
from app.tasks.scheduler import register_schedule, unregister_schedule

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=list[ScheduleRead])
async def list_schedules_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[ScheduleRead]:
    schedules = await list_schedules(db, skip=skip, limit=limit)
    return [ScheduleRead.model_validate(s) for s in schedules]


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
async def create_schedule_endpoint(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_operator_or_admin),
) -> ScheduleRead:
    try:
        schedule = await create_schedule(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Schedule name already exists"
        ) from exc
    register_schedule(schedule)
    return ScheduleRead.model_validate(schedule)


@router.get("/{schedule_id}", response_model=ScheduleRead)
async def get_schedule_endpoint(
    schedule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ScheduleRead:
    schedule = await get_schedule_by_id(db, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return ScheduleRead.model_validate(schedule)


@router.patch("/{schedule_id}", response_model=ScheduleRead)
async def update_schedule_endpoint(
    schedule_id: uuid.UUID,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_operator_or_admin),
) -> ScheduleRead:
    schedule = await get_schedule_by_id(db, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    try:
        schedule = await update_schedule(db, schedule, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    register_schedule(schedule)
    return ScheduleRead.model_validate(schedule)


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule_endpoint(
    schedule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    schedule = await get_schedule_by_id(db, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    sid = str(schedule.id)
    await delete_schedule(db, schedule)
    unregister_schedule(sid)
