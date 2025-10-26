"""
Modelo SQLAlchemy para a tabela de Usuários.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.db.database import Base

if TYPE_CHECKING:
    from src.infrastructure.models.refresh_token import RefreshToken
    from src.infrastructure.models.user_role import UserRole
    from src.infrastructure.models.classification import Classification


class User(Base):
    """
    Modelo para a tabela 'users'.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email único do usuário",
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Senha hasheada com Argon2id",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nome completo do usuário",
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Telefone do usuário (apenas dígitos)",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Se o usuário está ativo",
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se o email foi verificado",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Data de criação da conta",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Data da última atualização",
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Data do último login",
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

    deleted_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID do admin que deletou",
    )

    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        foreign_keys="UserRole.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    classifications: Mapped[List["Classification"]] = relationship(
        "Classification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_users_email_is_active", "email", "is_active"),
        Index("ix_users_email_is_deleted", "email", "is_deleted"),
    )

    def __repr__(self) -> str:
        """Representação string do modelo."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"

    def __str__(self) -> str:
        """String legível do modelo."""
        return f"{self.name} ({self.email})"

    def soft_delete(self, deleted_by_id: int | None = None) -> None:
        """Marca o usuário como deletado."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = deleted_by_id

    def restore(self) -> None:
        """Restaura um usuário soft deleted."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

    @property
    def is_active_record(self) -> bool:
        """Verifica se o registro está ativo (não deletado)."""
        return not self.is_deleted
