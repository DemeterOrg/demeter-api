"""
Módulo de exceções personalizadas e handlers da aplicação.

"""

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
from src.config.exceptions.handlers import (
    register_exception_handlers,
    demeter_exception_handler,
    validation_exception_handler,
)

__all__ = [
    "DemeterException",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "DatabaseError",
    "ExternalServiceError",
    "register_exception_handlers",
    "demeter_exception_handler",
    "validation_exception_handler",
]
