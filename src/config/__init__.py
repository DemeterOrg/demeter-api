"""
Módulo de configuração central da aplicação DEMETER.

Este módulo agrupa todas as configurações da aplicação, incluindo:
- Settings (variáveis de ambiente)
- Database (engine e sessões)
- Security (autenticação, autorização, passwords)
- Logging (logs estruturados)
- Exceptions (exceções customizadas e handlers)
- Dependencies (dependencies comuns do FastAPI)
"""

from src.config.settings import settings
from src.config.db.database import database, Base, DatabaseEngine
from src.config.db.dependencies import get_db, get_db_context, DbSessionDep

# Importações de segurança
from src.config.security.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_token,
)
from src.config.security.password import (
    get_password_hash,
    verify_password,
    validate_password_strength,
)

# Importações de logging
from src.config.logging.logger import (
    logger,
    get_logger,
    setup_logging,
)

# Importações de exceções
from src.config.exceptions.custom_exceptions import (
    DemeterException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
)
from src.config.exceptions.handlers import register_exception_handlers

# Importações de dependencies
from src.config.dependencies.common import (
    get_current_user,
    get_current_user_id,
    get_current_active_user,
    CurrentUser,
    CurrentUserId,
    CurrentActiveUser,
)

__all__ = [
    # Settings
    "settings",
    # Database
    "database",
    "Base",
    "DatabaseEngine",
    "get_db",
    "get_db_context",
    "DbSessionDep",
    # Security - Auth
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    # Security - Password
    "get_password_hash",
    "verify_password",
    "validate_password_strength",
    # Logging
    "logger",
    "get_logger",
    "setup_logging",
    # Exceptions
    "DemeterException",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "DatabaseError",
    "ExternalServiceError",
    "register_exception_handlers",
    # Dependencies
    "get_current_user",
    "get_current_user_id",
    "get_current_active_user",
    "CurrentUser",
    "CurrentUserId",
    "CurrentActiveUser",
]
