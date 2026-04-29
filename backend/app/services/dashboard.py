from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.host import Host
from app.models.inventory import Inventory
from app.models.job import Job, JobStatus
from app.models.schedule import Schedule
from app.schemas.dashboard import DashboardStats
from app.schemas.job import JobRead


async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    total_hosts = await db.scalar(select(func.count()).select_from(Host)) or 0
    total_inventories = await db.scalar(select(func.count()).select_from(Inventory)) or 0
    total_schedules = await db.scalar(select(func.count()).select_from(Schedule)) or 0
    total_jobs = await db.scalar(select(func.count()).select_from(Job)) or 0

    running_jobs = (
        await db.scalar(
            select(func.count()).select_from(Job).where(Job.status == JobStatus.running)
        )
        or 0
    )

    since = datetime.now(UTC) - timedelta(hours=24)
    failed_last_24h = (
        await db.scalar(
            select(func.count())
            .select_from(Job)
            .where(Job.status == JobStatus.failed, Job.created_at >= since)
        )
        or 0
    )

    recent_result = await db.execute(select(Job).order_by(Job.created_at.desc()).limit(10))
    recent_jobs = [JobRead.model_validate(j) for j in recent_result.scalars().all()]

    return DashboardStats(
        total_hosts=total_hosts,
        total_inventories=total_inventories,
        total_schedules=total_schedules,
        total_jobs=total_jobs,
        running_jobs=running_jobs,
        failed_last_24h=failed_last_24h,
        recent_jobs=recent_jobs,
    )
