import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, require_operator_or_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.job import JobCreate, JobRead, JobReadDetail
from app.services.jobs import create_job, delete_job, get_job_by_id, list_jobs
from app.tasks.jobs import run_playbook

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
async def list_jobs_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[JobRead]:
    jobs = await list_jobs(db, skip=skip, limit=limit)
    return [JobRead.model_validate(j) for j in jobs]


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job_endpoint(
    data: JobCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_operator_or_admin),
) -> JobRead:
    try:
        job = await create_job(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    run_playbook.delay(str(job.id))
    return JobRead.model_validate(job)


@router.get("/{job_id}", response_model=JobReadDetail)
async def get_job_endpoint(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> JobReadDetail:
    job = await get_job_by_id(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobReadDetail.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_endpoint(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    job = await get_job_by_id(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    await delete_job(db, job)
