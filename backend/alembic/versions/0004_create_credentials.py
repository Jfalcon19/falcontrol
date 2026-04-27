"""create credentials table

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "credentials",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "credential_type",
            sa.Enum("ssh_key", "ssh_password", "winrm", name="credentialtype"),
            nullable=False,
        ),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("encrypted_secret", sa.Text(), nullable=False),
        sa.Column("encrypted_passphrase", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_credentials_name"), "credentials", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_credentials_name"), table_name="credentials")
    op.drop_table("credentials")
    op.execute(sa.text("DROP TYPE IF EXISTS credentialtype"))
