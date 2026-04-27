import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.host import ConnectionType, OsType


class HostCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=255)
    description: str | None = None
    os_type: OsType
    connection_type: ConnectionType
    port: int | None = Field(default=None, ge=1, le=65535)
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def tags_max_length(cls, v: list[str]) -> list[str]:
        if len(v) > 20:
            raise ValueError("Tags list cannot exceed 20 elements")
        return v


class HostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    address: str
    description: str | None
    os_type: OsType
    connection_type: ConnectionType
    port: int | None
    tags: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class HostUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    os_type: OsType | None = None
    connection_type: ConnectionType | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    tags: list[str] | None = None
    is_active: bool | None = None

    @field_validator("tags")
    @classmethod
    def tags_max_length(cls, v: list[str] | None) -> list[str] | None:
        if v is not None and len(v) > 20:
            raise ValueError("Tags list cannot exceed 20 elements")
        return v
