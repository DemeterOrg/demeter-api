"""Modelo SQLAlchemy para associação Role-Permission."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.db.database import Base

if TYPE_CHECKING:
    from src.infrastructure.models.role import Role
    from src.infrastructure.models.permission import Permission


class RolePermission(Base):
    """Tabela de associação entre Roles e Permissions."""

    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        Index("ix_role_permissions_unique", "role_id", "permission_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
