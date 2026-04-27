"""create inventories and inventory_hosts tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inventories",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventories_name"), "inventories", ["name"], unique=True)

    op.create_table(
        "inventory_hosts",
        sa.Column("inventory_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("host_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["hosts.id"]),
        sa.ForeignKeyConstraint(["inventory_id"], ["inventories.id"]),
        sa.PrimaryKeyConstraint("inventory_id", "host_id"),
    )


def downgrade() -> None:
    op.drop_table("inventory_hosts")
    op.drop_index(op.f("ix_inventories_name"), table_name="inventories")
    op.drop_table("inventories")
