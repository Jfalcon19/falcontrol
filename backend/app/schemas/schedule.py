import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_cron(v: str) -> str:
    parts = v.strip().split()
    if len(parts) != 5:
        raise ValueError("cron_expression must have exactly 5 fields: minute hour day month weekday")  # noqa: E501
    return v.strip()


class ScheduleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    cron_expression: str = Field(min_length=9, max_length=128)
    inventory_id: uuid.UUID
    playbook_path: str = Field(min_length=1, max_length=512)
    enabled: bool = True

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v: str) -> str:
        return _validate_cron(v)


class ScheduleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=256)
    cron_expression: str | None = Field(default=None, min_length=9, max_length=128)
    inventory_id: uuid.UUID | None = None
    playbook_path: str | None = Field(default=None, min_length=1, max_length=512)
    enabled: bool | None = None

    @field_validator("cron_expression")
    @classmethod
    def validate_cron(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_cron(v)


class ScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    cron_expression: str
    inventory_id: uuid.UUID
    playbook_path: str
    enabled: bool
    created_at: datetime
    updated_at: datetime | None
