from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    configurações centrais da API.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "DEMETER-API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para classificaçãoo de grãos com IA"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = Field(default=True)

    DATABASE_URL: PostgresDsn = Field(
        ...,
        description="URL de conexãoo com PostgreSQL (asyncpg)"
    )

    DATABASE_ECHO: bool = Field(
        default=True,
        description="Habilitar logs SQL (apenas em development)"
    )

    DATABASE_POOL_SIZE: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Tamanho do pool de conexões"
    )

    DATABASE_MAX_OVERFLOW: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Máximo de conexões extras além do pool"
    )

    @field_validator("DATABASE_ECHO")
    @classmethod
    def validate_database_echo(cls, v: bool, info) -> bool:
        """Desabilita echo em produçãoo para performance"""
        if info.data.get("ENVIRONMENT") == "production":
            return False
        return v

    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Chave secreta para assinatura de tokens JWT"
    )

    ALGORITHM: str = Field(
        default="HS256",
        description="Algoritmo de criptografia JWT"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15,
        ge=5,
        le=60,
        description="Tempo de expiração do access token em minutos"
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Tempo de expiração do refresh token em dias"
    )

    PASSWORD_MIN_LENGTH: int = Field(
        default=8,
        ge=8,
        description="Tamanho mánimo da senha"
    )

    PASSWORD_REQUIRE_UPPERCASE: bool = Field(
        default=True,
        description="Exigir letra maiúscula na senha"
    )

    PASSWORD_REQUIRE_LOWERCASE: bool = Field(
        default=True,
        description="Exigir letra minúscula na senha"
    )

    PASSWORD_REQUIRE_DIGIT: bool = Field(
        default=True,
        description="Exigir número na senha"
    )

    PASSWORD_REQUIRE_SPECIAL: bool = Field(
        default=True,
        description="Exigir caractere especial na senha"
    )

    ALLOWED_ORIGINS: list[str] | str = Field(
        default=["http://localhost:3000"],
        description="Lista de origens permitidas para CORS"
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Converte string separada por vírgula em lista"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    ALLOWED_METHODS: list[str] | str = Field(
        default=["GET", "POST", "PATCH", "DELETE"],
        description="Motodos HTTP permitidos"
    )

    @field_validator("ALLOWED_METHODS", mode="before")
    @classmethod
    def parse_allowed_methods(cls, v):
        """Converte string separada por vírgula em lista"""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    ALLOWED_HEADERS: list[str] | str = Field(
        default=["Authorization", "Content-Type"],
        description="Headers permitidos"
    )

    @field_validator("ALLOWED_HEADERS", mode="before")
    @classmethod
    def parse_allowed_headers(cls, v):
        """Converte string separada por vírgula em lista"""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Permitir envio de cookies/credenciais"
    )

    RATE_LIMIT_LOGIN: str = Field(
        default="5/15minute",
        description="Rate limit para endpoint de login"
    )

    RATE_LIMIT_AUTHENTICATED: str = Field(
        default="100/minute",
        description="Rate limit para endpoints autenticados"
    )

    RATE_LIMIT_PUBLIC: str = Field(
        default="20/minute",
        description="Rate limit para endpoints p�blicos"
    )

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Nível de log"
    )

    LOG_FORMAT: Literal["json", "console"] = Field(
        default="console",
        description="Formato do log (json para produ��o, console para dev)"
    )

    LOG_DIR: str = Field(
        default="logs",
        description="Diretório para armazenar logs"
    )

    MAX_UPLOAD_SIZE: int = Field(
        default=10 * 1024 * 1024,
        description="Tamanho máximo de upload em bytes"
    )

    ALLOWED_IMAGE_TYPES: list[str] | str = Field(
        default=["image/jpeg", "image/png", "image/jpg"],
        description="Tipos de imagem permitidos"
    )

    @field_validator("ALLOWED_IMAGE_TYPES", mode="before")
    @classmethod
    def parse_allowed_image_types(cls, v):
        """Converte string separada por vírgula em lista"""
        if isinstance(v, str):
            return [img_type.strip() for img_type in v.split(",")]
        return v

    UPLOAD_DIR: str = Field(
        default="uploads",
        description="Diretório temporário para uploads"
    )

    USE_S3: bool = Field(
        default=False,
        description="Usar AWS S3 para armazenamento"
    )

    AWS_ACCESS_KEY_ID: str | None = Field(
        default=None,
        description="AWS Access Key ID"
    )

    AWS_SECRET_ACCESS_KEY: str | None = Field(
        default=None,
        description="AWS Secret Access Key"
    )

    AWS_REGION: str = Field(
        default="us-east-1",
        description="Região AWS"
    )

    S3_BUCKET_NAME: str | None = Field(
        default=None,
        description="Nome do bucket S3"
    )

    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return self.ENVIRONMENT == "production"

    @property
    def database_url_str(self) -> str:
        """Retorna a URL do banco como string"""
        return str(self.DATABASE_URL)

settings = Settings()
