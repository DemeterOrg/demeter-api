"""Modelo SQLAlchemy para Logs de Auditoria."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Index, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.db.database import Base

if TYPE_CHECKING:
    from src.infrastructure.models.user import User


class AuditLog(Base):
    """Modelo para logs de auditoria de ações sensíveis."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID do usuário que executou a ação",
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Ação executada (ex: delete_user, restore_classification)",
    )

    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo de recurso afetado (users, classifications, etc)",
    )

    resource_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="ID do recurso afetado",
    )

    changes: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Detalhes da mudança (before/after)",
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="Endereço IP do cliente",
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="User agent do cliente",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    user: Mapped["User | None"] = relationship("User")

    __table_args__ = (
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_created_at_desc", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}')>"

    def __str__(self) -> str:
        return f"AuditLog #{self.id} - {self.action} on {self.resource_type}"
