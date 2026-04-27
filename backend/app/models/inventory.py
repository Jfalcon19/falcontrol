from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.host import Host

inventory_hosts = Table(
    "inventory_hosts",
    Base.metadata,
    Column("inventory_id", Uuid(as_uuid=True), ForeignKey("inventories.id"), primary_key=True),
    Column("host_id", Uuid(as_uuid=True), ForeignKey("hosts.id"), primary_key=True),
)


class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    hosts: Mapped[list[Host]] = relationship("Host", secondary=inventory_hosts, lazy="selectin")

    def __repr__(self) -> str:
        return f"<Inventory id={self.id} name={self.name!r}>"
