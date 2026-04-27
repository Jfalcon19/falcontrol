import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.host import HostRead


class InventoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    host_ids: list[uuid.UUID] = Field(default_factory=list)


class InventoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    hosts: list[HostRead]
    created_at: datetime
    updated_at: datetime | None


class InventoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    host_ids: list[uuid.UUID] | None = None
