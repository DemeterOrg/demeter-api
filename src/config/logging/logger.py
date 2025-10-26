# -*- coding: utf-8 -*-
"""
Configuração de logging estruturado usando structlog.

Este módulo configura o sistema de logs da aplicação com formato JSON
estruturado para produção e formato colorido para desenvolvimento.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

import structlog
from pythonjsonlogger import jsonlogger

from src.config.settings import settings


def setup_logging() -> structlog.BoundLogger:
    """
    Configura o sistema de logging da aplicação.

    Retorna:
        Logger estruturado configurado

    Example:
        >>> logger = setup_logging()
        >>> logger.info("Application started", environment="production")
    """
    # Criar diretório de logs se não existir
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(exist_ok=True)

    # Configurar nível de log
    log_level = getattr(logging, settings.LOG_LEVEL.upper())

    # Configurar formatação baseada no ambiente
    if settings.LOG_FORMAT == "json":
        # Formato JSON para produção
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Formato console colorido para desenvolvimento
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # Configurar structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configurar handlers do logging padrão
    handlers = []

    # Handler para console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if settings.LOG_FORMAT == "json":
        # Formato JSON para console em produção
        json_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            timestamp=True,
        )
        console_handler.setFormatter(json_formatter)
    else:
        # Formato simples para desenvolvimento
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)

    handlers.append(console_handler)

    # Handler para arquivo (apenas em produção ou se configurado)
    if settings.ENVIRONMENT == "production" or settings.LOG_FORMAT == "json":
        # Arquivo com rotação diária
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "demeter-api.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)

        # Sempre usar JSON para arquivo
        json_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            timestamp=True,
        )
        file_handler.setFormatter(json_formatter)
        handlers.append(file_handler)

        # Arquivo separado para erros
        error_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "demeter-api-errors.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=10,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        handlers.append(error_handler)

    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remover handlers existentes para evitar duplicação
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Adicionar novos handlers
    for handler in handlers:
        root_logger.addHandler(handler)

    # Silenciar logs muito verbosos de bibliotecas externas
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Criar logger estruturado
    logger = structlog.get_logger()

    logger.info(
        "Logging system configured",
        log_level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        environment=settings.ENVIRONMENT,
    )

    return logger


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Obtém um logger nomeado.

    Args:
        name: Nome do logger (geralmente __name__ do módulo)

    Returns:
        Logger estruturado

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Operation completed", user_id=123)
    """
    return structlog.get_logger(name)


def log_request(
    logger: structlog.BoundLogger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **kwargs: Any,
) -> None:
    """
    Loga uma requisição HTTP.

    Args:
        logger: Logger estruturado
        method: Método HTTP (GET, POST, etc.)
        path: Caminho da requisição
        status_code: Código de status HTTP
        duration_ms: Duração da requisição em milissegundos
        **kwargs: Informações adicionais (user_id, ip, etc.)

    Example:
        >>> logger = get_logger(__name__)
        >>> log_request(
        ...     logger,
        ...     method="POST",
        ...     path="/api/v1/users",
        ...     status_code=201,
        ...     duration_ms=123.45,
        ...     user_id=456,
        ... )
    """
    log_data = {
        "event": "http_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        **kwargs,
    }

    if status_code >= 500:
        logger.error("HTTP request failed", **log_data)
    elif status_code >= 400:
        logger.warning("HTTP request client error", **log_data)
    else:
        logger.info("HTTP request completed", **log_data)


def log_auth_event(
    logger: structlog.BoundLogger,
    event_type: str,
    user_id: int | None = None,
    email: str | None = None,
    success: bool = True,
    reason: str | None = None,
    **kwargs: Any,
) -> None:
    """
    Loga eventos de autenticação.

    Args:
        logger: Logger estruturado
        event_type: Tipo do evento (login, logout, register, etc.)
        user_id: ID do usuário
        email: Email do usuário
        success: Se a operação foi bem-sucedida
        reason: Motivo de falha (se aplicável)
        **kwargs: Informações adicionais

    Example:
        >>> logger = get_logger(__name__)
        >>> log_auth_event(
        ...     logger,
        ...     event_type="login",
        ...     user_id=123,
        ...     email="user@example.com",
        ...     success=True,
        ...     ip="192.168.1.1",
        ... )
    """
    log_data = {
        "event": "auth_event",
        "event_type": event_type,
        "success": success,
        **kwargs,
    }

    if user_id:
        log_data["user_id"] = user_id
    if email:
        log_data["email"] = email
    if reason:
        log_data["reason"] = reason

    if success:
        logger.info(f"Authentication event: {event_type}", **log_data)
    else:
        logger.warning(f"Authentication failed: {event_type}", **log_data)


def log_database_operation(
    logger: structlog.BoundLogger,
    operation: str,
    table: str,
    success: bool = True,
    duration_ms: float | None = None,
    record_id: int | None = None,
    **kwargs: Any,
) -> None:
    """
    Loga operações de banco de dados.

    Args:
        logger: Logger estruturado
        operation: Tipo de operação (insert, update, delete, select)
        table: Nome da tabela
        success: Se a operação foi bem-sucedida
        duration_ms: Duração da operação em milissegundos
        record_id: ID do registro afetado
        **kwargs: Informações adicionais

    Example:
        >>> logger = get_logger(__name__)
        >>> log_database_operation(
        ...     logger,
        ...     operation="insert",
        ...     table="users",
        ...     success=True,
        ...     duration_ms=45.2,
        ...     record_id=123,
        ... )
    """
    log_data = {
        "event": "database_operation",
        "operation": operation,
        "table": table,
        "success": success,
        **kwargs,
    }

    if duration_ms:
        log_data["duration_ms"] = round(duration_ms, 2)
    if record_id:
        log_data["record_id"] = record_id

    if success:
        logger.debug(f"Database operation: {operation} on {table}", **log_data)
    else:
        logger.error(f"Database operation failed: {operation} on {table}", **log_data)


# Logger global da aplicação
logger = setup_logging()
