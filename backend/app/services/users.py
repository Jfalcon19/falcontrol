import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.services.auth import hash_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    data: UserCreate,
    role: UserRole | None = None,
) -> User:
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=role if role is not None else data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def ensure_first_admin(db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.role == UserRole.admin).limit(1))
    if result.scalar_one_or_none() is None:
        from app.core.config import settings

        admin = User(
            email=settings.first_admin_email,
            hashed_password=hash_password(settings.first_admin_password),
            role=UserRole.admin,
        )
        db.add(admin)
        await db.commit()
