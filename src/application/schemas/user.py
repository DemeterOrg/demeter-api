"""
Schemas Pydantic para usuários.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from src.config.settings import settings


class UserBase(BaseModel):
    """
    Schema base para usuário com campos comuns.
    """

    email: EmailStr = Field(
        ...,
        description="Email do usuário",
        examples=["usuario@example.com"],
    )

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome completo do usuário",
        examples=["João Silva"],
    )

    phone: str = Field(
        ...,
        min_length=10,
        max_length=11,
        description="Telefone do usuário (apenas dígitos)",
        examples=["11987654321"],
        pattern=r"^\d{10,11}$",
    )


class UserCreate(UserBase):
    """
    Schema para criação de usuário.
    """

    password: str = Field(
        ...,
        min_length=settings.PASSWORD_MIN_LENGTH,
        max_length=128,
        description="Senha do usuário",
    )

    password_confirm: str = Field(
        ...,
        min_length=settings.PASSWORD_MIN_LENGTH,
        max_length=128,
        description="Confirmação da senha",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Valida força da senha usando configurações do settings."""
        from src.config.security.password import validate_password_strength

        is_valid, error_message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_message)
        return v

    @field_validator("password_confirm")
    @classmethod
    def validate_password_match(cls, v: str, info) -> str:
        """Valida se a confirmação de senha corresponde à senha."""
        password = info.data.get("password")
        if password and v != password:
            raise ValueError("As senhas não correspondem")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida o nome do usuário."""
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")

        if len(v.strip()) < 2:
            raise ValueError("Nome deve ter no mínimo 2 caracteres")

        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("Nome deve conter apenas letras e espaços")

        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Valida o telefone do usuário (apenas dígitos)."""
        phone_digits = re.sub(r'\D', '', v)

        if len(phone_digits) < 10 or len(phone_digits) > 11:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")

        return phone_digits

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "joao.silva@example.com",
                    "name": "João Silva",
                    "phone": "11987654321",
                    "password": "MinhasenhaSegura123!",
                    "password_confirm": "MinhasenhaSegura123!",
                }
            ]
        }
    }


class UserUpdate(BaseModel):
    """
    Schema para atualização de usuário.
    """

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Nome completo do usuário",
    )

    email: Optional[EmailStr] = Field(
        default=None,
        description="Email do usuário",
    )

    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=11,
        description="Telefone do usuário (apenas dígitos)",
        pattern=r"^\d{10,11}$",
    )

    password: Optional[str] = Field(
        default=None,
        min_length=settings.PASSWORD_MIN_LENGTH,
        max_length=128,
        description="Nova senha do usuário",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Valida força da senha se fornecida."""
        if v is None:
            return v

        from src.config.security.password import validate_password_strength

        is_valid, error_message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_message)
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Valida o nome se fornecido."""
        if v is None:
            return v

        if not v.strip():
            raise ValueError("Nome não pode ser vazio")

        if len(v.strip()) < 2:
            raise ValueError("Nome deve ter no mínimo 2 caracteres")

        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("Nome deve conter apenas letras e espaços")

        return v.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Valida o telefone se fornecido."""
        if v is None:
            return v

        phone_digits = re.sub(r'\D', '', v)

        if len(phone_digits) < 10 or len(phone_digits) > 11:
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")

        return phone_digits

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "João Silva Santos",
                    "email": "joao.santos@example.com",
                    "phone": "11987654321",
                }
            ]
        }
    }


class UserResponse(UserBase):
    """
    Schema para resposta com dados do usuário.
    """

    id: int = Field(..., description="ID do usuário")
    is_active: bool = Field(..., description="Se o usuário está ativo")
    is_verified: bool = Field(..., description="Se o email foi verificado")
    created_at: datetime = Field(..., description="Data de criação da conta")
    last_login: Optional[datetime] = Field(None, description="Data do último login")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "email": "joao.silva@example.com",
                    "name": "João Silva",
                    "phone": "11987654321",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2025-10-23T10:00:00Z",
                    "last_login": "2025-10-23T15:30:00Z",
                }
            ]
        }
    }


class UserInDB(UserResponse):
    """
    Schema para usuário com senha hasheada (uso interno).
    """

    hashed_password: str = Field(..., description="Senha hasheada")

    model_config = {
        "from_attributes": True,
    }


class UserListResponse(BaseModel):
    """
    Schema para resposta de listagem de usuários com paginação.
    """

    users: list[UserResponse] = Field(..., description="Lista de usuários")
    total: int = Field(..., description="Total de usuários")
    skip: int = Field(..., description="Offset usado na busca")
    limit: int = Field(..., description="Limite usado na busca")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "users": [
                        {
                            "id": 1,
                            "email": "joao@example.com",
                            "name": "João Silva",
                            "phone": "11987654321",
                            "is_active": True,
                            "is_verified": True,
                            "created_at": "2025-10-23T10:00:00Z",
                            "last_login": "2025-10-23T15:30:00Z",
                        }
                    ],
                    "total": 1,
                    "skip": 0,
                    "limit": 100,
                }
            ]
        }
    }
