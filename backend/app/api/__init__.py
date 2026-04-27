from app.api.auth import router as auth_router
from app.api.credentials import router as credentials_router
from app.api.hosts import router as hosts_router
from app.api.inventories import router as inventories_router
from app.api.users import router as users_router

__all__ = [
    "auth_router",
    "credentials_router",
    "hosts_router",
    "inventories_router",
    "users_router",
]
