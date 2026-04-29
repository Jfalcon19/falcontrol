"""Celery Beat startup hook — syncs DB schedules into RedBeat on worker start."""

from celery.signals import beat_init

from app.tasks.celery_app import celery_app  # noqa: F401 — ensures app is configured


@beat_init.connect  # type: ignore[untyped-decorator]
def on_beat_init(sender: object, **kwargs: object) -> None:
    from app.tasks.scheduler import sync_all_schedules

    sync_all_schedules()
