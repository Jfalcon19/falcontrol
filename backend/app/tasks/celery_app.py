from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "falcontrol",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    # RedBeat — dynamic cron scheduler backed by Redis
    beat_scheduler="redbeat.RedBeatScheduler",
    redbeat_redis_url=settings.redis_url,
    redbeat_key_prefix="falcontrol:beat:",
)
