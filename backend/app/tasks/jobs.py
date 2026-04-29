from app.tasks.celery_app import celery_app


@celery_app.task(name="run_playbook")  # type: ignore[untyped-decorator]
def run_playbook(job_id: str) -> None:
    """Execute an Ansible playbook for the given job. Implemented in issue #17."""
