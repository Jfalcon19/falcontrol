from pydantic import BaseModel

from app.schemas.job import JobRead


class DashboardStats(BaseModel):
    total_hosts: int
    total_inventories: int
    total_schedules: int
    total_jobs: int
    running_jobs: int
    failed_last_24h: int
    recent_jobs: list[JobRead]
