"""Modelo SQLAlchemy para Permissions (Permissões)."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.db.database import Base

if TYPE_CHECKING:
    from src.infrastructure.models.role_permission import RolePermission


class Permission(Base):
    """Modelo para permissões do sistema."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Nome único (formato: resource:action:scope)",
    )

    resource: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Recurso (users, classifications, roles)",
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Ação (create, read, update, delete, restore)",
    )

    scope: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Escopo (own, all)",
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Descrição da permissão",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_permissions_resource_action_scope", "resource", "action", "scope", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name='{self.name}')>"

    def __str__(self) -> str:
        return self.name
