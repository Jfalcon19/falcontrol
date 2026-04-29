import asyncio
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import ansible_runner
import redis as redis_lib

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.inventory_writer import generate_inventory_ini
from app.services.jobs import get_job_by_id, mark_finished, mark_running
from app.tasks.celery_app import celery_app


def _redis_client() -> redis_lib.Redis:
    return redis_lib.Redis.from_url(settings.redis_url, decode_responses=True)


def _channel(job_id: str) -> str:
    return f"job:{job_id}:logs"


async def _fetch_job_data(job_id: str) -> tuple[str, str]:
    """Mark job running; return (playbook_path, inventory_ini)."""
    async with AsyncSessionLocal() as db:
        job = await get_job_by_id(db, uuid.UUID(job_id))
        if job is None:
            raise RuntimeError(f"Job {job_id} not found")
        await mark_running(db, job)
        return job.playbook_path, generate_inventory_ini(job.inventory)


async def _save_result(job_id: str, *, return_code: int, stdout: str) -> None:
    async with AsyncSessionLocal() as db:
        job = await get_job_by_id(db, uuid.UUID(job_id))
        if job is not None:
            await mark_finished(db, job, return_code=return_code, stdout=stdout)


@celery_app.task(name="run_playbook")  # type: ignore[untyped-decorator]
def run_playbook(job_id: str) -> None:
    r = _redis_client()
    channel = _channel(job_id)

    try:
        playbook_path, inventory_ini = asyncio.run(_fetch_job_data(job_id))
    except Exception as exc:  # noqa: BLE001
        r.publish(channel, f"ERROR: {exc}")
        r.publish(channel, "__END__")
        return

    stdout_lines: list[str] = []

    def event_handler(event: dict[str, Any]) -> None:
        line: str = event.get("stdout", "")
        if line:
            stdout_lines.append(line)
            r.publish(channel, line)

    with TemporaryDirectory() as tmpdir:
        inv_path = Path(tmpdir) / "inventory.ini"
        inv_path.write_text(inventory_ini)

        project_dir = Path(tmpdir) / "project"
        project_dir.mkdir()

        pb = Path(playbook_path)
        if pb.is_absolute():
            pb_link = project_dir / pb.name
            pb_link.symlink_to(pb)
            playbook_name = pb.name
        else:
            playbook_name = playbook_path

        result: Any = ansible_runner.run(
            private_data_dir=tmpdir,
            playbook=playbook_name,
            inventory=str(inv_path),
            event_handler=event_handler,
            quiet=True,
        )
        return_code: int = result.rc
        stdout = "\n".join(stdout_lines)

    asyncio.run(_save_result(job_id, return_code=return_code, stdout=stdout))
    r.publish(channel, "__END__")
