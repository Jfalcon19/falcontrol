"""RedBeat integration — registers Schedule ORM objects as Celery periodic tasks."""

import asyncio

from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry

from app.core.database import AsyncSessionLocal
from app.models.schedule import Schedule
from app.tasks.celery_app import celery_app


def _cron(expr: str) -> crontab:
    minute, hour, day_of_month, month_of_year, day_of_week = expr.split()
    return crontab(
        minute=minute,
        hour=hour,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
        day_of_week=day_of_week,
    )


def _key(schedule_id: str) -> str:
    return f"falcontrol:schedule:{schedule_id}"


def register_schedule(schedule: Schedule) -> None:
    """Upsert a periodic task entry in RedBeat for the given schedule."""
    entry = RedBeatSchedulerEntry(
        name=_key(str(schedule.id)),
        task="run_scheduled_job",
        schedule=_cron(schedule.cron_expression),
        args=[str(schedule.id)],
        enabled=schedule.enabled,
        app=celery_app,
    )
    entry.save()


def unregister_schedule(schedule_id: str) -> None:
    """Remove a periodic task entry from RedBeat, ignoring missing entries."""
    try:
        entry = RedBeatSchedulerEntry.from_key(_key(schedule_id), app=celery_app)
        entry.delete()
    except Exception:  # noqa: BLE001
        pass


async def _load_all_schedules() -> list[Schedule]:
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        result = await db.execute(select(Schedule))
        return list(result.scalars().all())


def sync_all_schedules() -> None:
    """Called on Beat worker startup to sync all DB schedules into RedBeat."""
    schedules = asyncio.run(_load_all_schedules())
    for schedule in schedules:
        if schedule.enabled:
            register_schedule(schedule)
        else:
            unregister_schedule(str(schedule.id))
