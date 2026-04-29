from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth_router,
    credentials_router,
    hosts_router,
    inventories_router,
    jobs_router,
    schedules_router,
    users_router,
)
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.users import ensure_first_admin
from app.websockets.job_logs import router as job_logs_router


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    async with AsyncSessionLocal() as db:
        await ensure_first_admin(db)
    yield


app = FastAPI(
    title="Falcontrol API",
    version=settings.version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(hosts_router, prefix="/api")
app.include_router(inventories_router, prefix="/api")
app.include_router(credentials_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(schedules_router, prefix="/api")
app.include_router(job_logs_router, prefix="/ws")


@app.get("/api/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.version}
