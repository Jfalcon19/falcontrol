import asyncio
import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.job import JobStatus
from app.services.auth import decode_token
from app.services.jobs import get_job_by_id

router = APIRouter()

_SENTINEL = "__END__"
_KEEPALIVE_INTERVAL = 25.0  # seconds between pings when idle


@router.websocket("/jobs/{job_id}/logs")
async def job_logs(
    websocket: WebSocket,
    job_id: uuid.UUID,
    token: str | None = None,
) -> None:
    # ── Auth ──────────────────────────────────────────────────────────────
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("not an access token")
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await websocket.accept()

    # ── Check if job already finished ─────────────────────────────────────
    async with AsyncSessionLocal() as db:
        job = await get_job_by_id(db, job_id)
        if job is None:
            await websocket.send_text("__ERROR__: Job not found")
            await websocket.close()
            return
        if job.status in (JobStatus.success, JobStatus.failed):
            if job.stdout:
                for line in job.stdout.splitlines():
                    await websocket.send_text(line)
            await websocket.send_text(_SENTINEL)
            await websocket.close()
            return

    # ── Stream live from Redis pub/sub ────────────────────────────────────
    r: aioredis.Redis = aioredis.Redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub()
    channel = f"job:{job_id}:logs"
    await pubsub.subscribe(channel)
    try:
        while True:
            try:
                message = await asyncio.wait_for(
                    pubsub.get_message(ignore_subscribe_messages=True),
                    timeout=_KEEPALIVE_INTERVAL,
                )
            except TimeoutError:
                await websocket.send_text("__PING__")
                continue

            if message is None:
                await asyncio.sleep(0.05)
                continue

            data: str = message["data"]
            if data == _SENTINEL:
                await websocket.send_text(_SENTINEL)
                break
            await websocket.send_text(data)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await r.aclose()
