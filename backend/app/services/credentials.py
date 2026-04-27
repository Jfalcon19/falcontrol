import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.credential import Credential
from app.schemas.credential import CredentialCreate, CredentialUpdate
from app.services.vault import encrypt


async def get_credential_by_id(db: AsyncSession, credential_id: uuid.UUID) -> Credential | None:
    result = await db.execute(select(Credential).where(Credential.id == credential_id))
    return result.scalar_one_or_none()


async def get_credential_by_name(db: AsyncSession, name: str) -> Credential | None:
    result = await db.execute(select(Credential).where(Credential.name == name))
    return result.scalar_one_or_none()


async def list_credentials(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Credential]:
    result = await db.execute(
        select(Credential).order_by(Credential.name).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def create_credential(db: AsyncSession, data: CredentialCreate) -> Credential:
    credential = Credential(
        name=data.name,
        description=data.description,
        credential_type=data.credential_type,
        username=data.username,
        encrypted_secret=encrypt(data.secret),
        encrypted_passphrase=encrypt(data.passphrase) if data.passphrase else None,
    )
    db.add(credential)
    await db.commit()
    await db.refresh(credential)
    return credential


async def update_credential(
    db: AsyncSession, credential: Credential, data: CredentialUpdate
) -> Credential:
    if data.name is not None:
        credential.name = data.name
    if data.description is not None:
        credential.description = data.description
    if data.username is not None:
        credential.username = data.username
    if data.secret is not None:
        credential.encrypted_secret = encrypt(data.secret)
    if data.passphrase is not None:
        credential.encrypted_passphrase = encrypt(data.passphrase)
    await db.commit()
    await db.refresh(credential)
    return credential


async def delete_credential(db: AsyncSession, credential: Credential) -> None:
    await db.delete(credential)
    await db.commit()
