"""
Módulo de configuração central da aplicação DEMETER.
"""

from src.config.settings import settings
from src.config.db.database import database, Base, DatabaseEngine
from src.config.db.dependencies import get_db, get_db_context, DbSessionDep

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

from src.config.logging.logger import (
    logger,
    get_logger,
    setup_logging,
)

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

from src.config.dependencies.common import (
    get_current_user,
    get_current_user_id,
    get_current_active_user,
    CurrentUser,
    CurrentUserId,
    CurrentActiveUser,
)

__all__ = [
    "settings",
    "database",
    "Base",
    "DatabaseEngine",
    "get_db",
    "get_db_context",
    "DbSessionDep",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "get_password_hash",
    "verify_password",
    "validate_password_strength",
    "logger",
    "get_logger",
    "setup_logging",
    "DemeterException",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "DatabaseError",
    "ExternalServiceError",
    "register_exception_handlers",
    "get_current_user",
    "get_current_user_id",
    "get_current_active_user",
    "CurrentUser",
    "CurrentUserId",
    "CurrentActiveUser",
]
