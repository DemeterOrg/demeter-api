"""
Módulo de logging estruturado da aplicação.

Este módulo configura o sistema de logs usando structlog,
com suporte a formato JSON para produção e formato colorido
para desenvolvimento.
"""

from src.config.logging.logger import (
    setup_logging,
    get_logger,
    logger,
    log_request,
    log_auth_event,
    log_database_operation,
)

__all__ = [
    "setup_logging",
    "get_logger",
    "logger",
    "log_request",
    "log_auth_event",
    "log_database_operation",
]
