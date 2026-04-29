"""create schedules table

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "schedules",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("cron_expression", sa.String(128), nullable=False),
        sa.Column("inventory_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("playbook_path", sa.String(512), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["inventory_id"], ["inventories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_schedules_name"),
    )
    op.create_index("ix_schedules_name", "schedules", ["name"])
    op.create_index("ix_schedules_inventory_id", "schedules", ["inventory_id"])


def downgrade() -> None:
    op.drop_index("ix_schedules_inventory_id", table_name="schedules")
    op.drop_index("ix_schedules_name", table_name="schedules")
    op.drop_table("schedules")
