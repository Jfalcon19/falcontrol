import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate


async def create_job(db: AsyncSession, data: JobCreate) -> Job:
    inv = await db.get(Inventory, data.inventory_id)
    if inv is None:
        raise ValueError("inventory not found")
    job = Job(inventory_id=data.inventory_id, playbook_path=data.playbook_path)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def list_jobs(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Job]:
    result = await db.execute(
        select(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_job_by_id(db: AsyncSession, job_id: uuid.UUID) -> Job | None:
    return await db.get(Job, job_id)


async def delete_job(db: AsyncSession, job: Job) -> None:
    await db.delete(job)
    await db.commit()


async def mark_running(db: AsyncSession, job: Job) -> Job:
    job.status = JobStatus.running
    job.started_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(job)
    return job


async def mark_finished(
    db: AsyncSession,
    job: Job,
    *,
    return_code: int,
    stdout: str,
) -> Job:
    job.status = JobStatus.success if return_code == 0 else JobStatus.failed
    job.return_code = return_code
    job.stdout = stdout
    job.finished_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(job)
    return job
