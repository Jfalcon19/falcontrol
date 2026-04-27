import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.credential import CredentialType


class CredentialCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    credential_type: CredentialType
    username: str | None = Field(default=None, max_length=255)
    secret: str = Field(min_length=1)
    passphrase: str | None = None

    @model_validator(mode="after")
    def username_required_for_password_types(self) -> "CredentialCreate":
        needs_username = self.credential_type in (CredentialType.ssh_password, CredentialType.winrm)
        if needs_username and not self.username:
            raise ValueError("username is required for ssh_password and winrm credentials")
        return self


class CredentialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    credential_type: CredentialType
    username: str | None
    created_at: datetime
    updated_at: datetime | None


class CredentialUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    username: str | None = Field(default=None, max_length=255)
    secret: str | None = Field(default=None, min_length=1)
    passphrase: str | None = None
