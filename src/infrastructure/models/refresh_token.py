"""
Modelo SQLAlchemy para a tabela de Refresh Tokens.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.db.database import Base

if TYPE_CHECKING:
    from src.infrastructure.models.user import User


class RefreshToken(Base):
    """
    Modelo para a tabela 'refresh_tokens'.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    token: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
        index=True,
        comment="Hash do refresh token",
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID do usuário proprietário",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Data de expiração do token",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Data de criação do token",
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data de revogação do token",
    )

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Se o token foi revogado",
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User agent do cliente",
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="Endereço IP do cliente",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
    )

    __table_args__ = (
        Index("ix_refresh_tokens_user_is_revoked", "user_id", "is_revoked"),
        Index("ix_refresh_tokens_expires_is_revoked", "expires_at", "is_revoked"),
    )

    def __repr__(self) -> str:
        """Representação string do modelo."""
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"

    def __str__(self) -> str:
        """String legível do modelo."""
        status = "revoked" if self.is_revoked else "active"
        return f"RefreshToken #{self.id} ({status})"

    @property
    def is_expired(self) -> bool:
        """Verifica se o token está expirado."""
        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Verifica se o token é válido (não revogado e não expirado)."""
        return not self.is_revoked and not self.is_expired

    def revoke(self) -> None:
        """Revoga o token."""
        self.is_revoked = True
        self.revoked_at = datetime.now(timezone.utc)
