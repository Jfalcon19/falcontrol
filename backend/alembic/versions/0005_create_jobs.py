"""create jobs table

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("inventory_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("playbook_path", sa.String(512), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "running", "success", "failed", name="jobstatus"),
            nullable=False,
        ),
        sa.Column("stdout", sa.Text(), nullable=True),
        sa.Column("return_code", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["inventory_id"], ["inventories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_inventory_id", "jobs", ["inventory_id"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_created_at", "jobs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_jobs_created_at", table_name="jobs")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_index("ix_jobs_inventory_id", table_name="jobs")
    op.drop_table("jobs")
    op.execute(sa.text("DROP TYPE IF EXISTS jobstatus"))
