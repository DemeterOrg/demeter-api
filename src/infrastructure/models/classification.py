"""Modelo SQLAlchemy para Classificações de Grãos."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import String, DateTime, ForeignKey, Boolean, Index, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.db.database import Base

if TYPE_CHECKING:
    from src.infrastructure.models.user import User


class Classification(Base):
    """Modelo para classificações de grãos."""

    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID do usuário que criou a classificação",
    )

    image_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Caminho da imagem armazenada",
    )

    grain_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Tipo de grão classificado",
    )

    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
        comment="Score de confiança da IA (0.0000 a 1.0000)",
    )

    extra_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Dados adicionais da classificação",
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Soft delete flag",
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data da exclusão",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="classifications")

    __table_args__ = (
        Index("ix_classifications_user_is_deleted", "user_id", "is_deleted"),
        Index("ix_classifications_created_at_desc", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Classification(id={self.id}, user_id={self.user_id}, grain='{self.grain_type}')>"

    def __str__(self) -> str:
        return f"Classification #{self.id} - {self.grain_type}"

    def soft_delete(self) -> None:
        """Marca a classificação como deletada."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restaura uma classificação soft deleted."""
        self.is_deleted = False
        self.deleted_at = None

    @property
    def is_active_record(self) -> bool:
        """Verifica se o registro está ativo (não deletado)."""
        return not self.is_deleted
