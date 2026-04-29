import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.job import JobStatus


class JobCreate(BaseModel):
    inventory_id: uuid.UUID
    playbook_path: str = Field(min_length=1, max_length=512)


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inventory_id: uuid.UUID
    playbook_path: str
    status: JobStatus
    return_code: int | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class JobReadDetail(JobRead):
    stdout: str | None
