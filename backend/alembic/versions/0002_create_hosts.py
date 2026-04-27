"""create hosts table

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "hosts",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "os_type",
            sa.Enum("linux", "windows", name="ostype"),
            nullable=False,
        ),
        sa.Column(
            "connection_type",
            sa.Enum("ssh", "winrm", name="connectiontype"),
            nullable=False,
        ),
        sa.Column("port", sa.Integer(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_hosts_name"), "hosts", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_hosts_name"), table_name="hosts")
    op.drop_table("hosts")
    op.execute(sa.text("DROP TYPE IF EXISTS ostype"))
    op.execute(sa.text("DROP TYPE IF EXISTS connectiontype"))
