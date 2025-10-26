"""Modelo SQLAlchemy para Roles (Papéis de Usuário)."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Boolean, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.db.database import Base

if TYPE_CHECKING:
    from src.infrastructure.models.user_role import UserRole
    from src.infrastructure.models.role_permission import RolePermission


class Role(Base):
    """Modelo para roles do sistema (admin, classificador)."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Nome único da role (ex: admin, classificador)",
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Descrição da role",
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se é role do sistema (não pode ser deletada)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"

    def __str__(self) -> str:
        return self.name
