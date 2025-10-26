"""
Entidade de domínio para User.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


@dataclass
class UserEntity:
    """
    Entidade de domínio representando um Usuário.
    """

    email: str
    name: str
    hashed_password: str
    phone: str
    id: Optional[int] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Valida os dados após inicialização."""
        self._validate()

    def _validate(self) -> None:
        """
        Valida as regras de negócio da entidade.

        Raises:
            ValueError: Se alguma validação falhar
        """
        if not self.email:
            raise ValueError("Email é obrigatório")

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValueError("Email inválido")

        if len(self.email) > 255:
            raise ValueError("Email deve ter no máximo 255 caracteres")

        if not self.name:
            raise ValueError("Nome é obrigatório")

        if len(self.name) < 2:
            raise ValueError("Nome deve ter no mínimo 2 caracteres")

        if len(self.name) > 100:
            raise ValueError("Nome deve ter no máximo 100 caracteres")

        if not self.hashed_password:
            raise ValueError("Senha hasheada é obrigatória")

        if not self.phone:
            raise ValueError("Telefone é obrigatório")

        # Remove caracteres não numéricos para validação
        phone_digits = re.sub(r'\D', '', self.phone)

        if len(phone_digits) < 10 or len(phone_digits) > 11:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")

    def activate(self) -> None:
        """Ativa o usuário."""
        self.is_active = True

    def deactivate(self) -> None:
        """Desativa o usuário."""
        self.is_active = False

    def verify_email(self) -> None:
        """Marca o email como verificado."""
        self.is_verified = True

    def update_last_login(self, login_time: datetime) -> None:
        """
        Atualiza a data do último login.

        Args:
            login_time: Data/hora do login
        """
        self.last_login = login_time

    def __str__(self) -> str:
        """Representação string da entidade."""
        return f"{self.name} ({self.email})"

    def __repr__(self) -> str:
        """Representação detalhada da entidade."""
        return (
            f"UserEntity(id={self.id}, email='{self.email}', "
            f"name='{self.name}', phone='{self.phone}')"
        )
