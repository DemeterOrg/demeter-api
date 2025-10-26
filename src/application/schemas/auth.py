"""
Schemas Pydantic para autenticação.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    Schema para requisição de login.

    Attributes:
        email: Email do usuário
        password: Senha em texto plano
    """

    email: EmailStr = Field(
        ...,
        description="Email do usuário",
        examples=["usuario@example.com"],
    )

    password: str = Field(
        ...,
        min_length=1,
        description="Senha do usuário",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "usuario@example.com",
                    "password": "MinhasenhaSegura123!",
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """
    Schema para resposta de tokens.
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_in: int = Field(..., description="Tempo de expiração em segundos")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 900,
                }
            ]
        }
    }


class LoginResponse(BaseModel):
    """
    Schema para resposta de login bem-sucedido.
    """

    user: dict = Field(..., description="Dados do usuário")
    tokens: TokenResponse = Field(..., description="Tokens de autenticação")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user": {
                        "id": 1,
                        "email": "usuario@example.com",
                        "name": "João Silva",
                    },
                    "tokens": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 900,
                    },
                }
            ]
        }
    }


class RefreshTokenRequest(BaseModel):
    """
    Schema para requisição de renovação de token.
    """

    refresh_token: str = Field(
        ...,
        min_length=1,
        description="Refresh token",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                }
            ]
        }
    }


class LogoutRequest(BaseModel):
    """
    Schema para requisição de logout.
    """

    refresh_token: str | None = Field(
        default=None,
        description="Refresh token a ser revogado",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """
    Schema para resposta simples com mensagem.
    """

    message: str = Field(..., description="Mensagem de resposta")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Logout realizado com sucesso",
                }
            ]
        }
    }
