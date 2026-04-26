from app.core.config import settings
from app.services.auth import verify_password
from app.services.users import ensure_first_admin, get_user_by_email


async def test_ensure_first_admin_creates_admin(db_session) -> None:
    await ensure_first_admin(db_session)
    user = await get_user_by_email(db_session, settings.first_admin_email)
    assert user is not None
    assert user.role.value == "admin"
    assert user.is_active is True


async def test_ensure_first_admin_password_matches_settings(db_session) -> None:
    await ensure_first_admin(db_session)
    user = await get_user_by_email(db_session, settings.first_admin_email)
    assert user is not None
    assert verify_password(settings.first_admin_password, user.hashed_password), (
        "El hash almacenado no verifica contra settings.first_admin_password — "
        "comprueba que FALCONTROL_FIRST_ADMIN_PASSWORD se lee correctamente"
    )


async def test_ensure_first_admin_is_idempotent(db_session) -> None:
    await ensure_first_admin(db_session)
    await ensure_first_admin(db_session)  # segunda llamada no debe crear duplicado
    from sqlalchemy import func, select

    from app.models.user import User, UserRole

    result = await db_session.execute(select(func.count()).where(User.role == UserRole.admin))
    assert result.scalar_one() == 1
