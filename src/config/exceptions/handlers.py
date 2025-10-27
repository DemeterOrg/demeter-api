"""
Handlers globais de exceções para o FastAPI.
"""

from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose.exceptions import JWTError, ExpiredSignatureError
from sqlalchemy.exc import SQLAlchemyError

from src.config.exceptions.custom_exceptions import DemeterException
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


async def demeter_exception_handler(
    request: Request,
    exc: DemeterException,
) -> JSONResponse:
    """
    Handler para exceções personalizadas da aplicação (DemeterException).
    """
    logger.warning(
        "Application exception",
        exception_type=exc.__class__.__name__,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        details=exc.details,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handler para erros de validação do Pydantic.
    """
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(
        "Validation error",
        path=request.url.path,
        method=request.method,
        errors=errors,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Erro de validação nos dados fornecidos",
            "details": errors,
        },
    )


async def jwt_exception_handler(
    request: Request,
    exc: Union[JWTError, ExpiredSignatureError],
) -> JSONResponse:
    """
    Handler para erros de JWT.
    """
    logger.warning(
        "JWT error",
        exception_type=exc.__class__.__name__,
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )

    if isinstance(exc, ExpiredSignatureError):
        message = "Token expirado"
    else:
        message = "Token inválido"

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "AuthenticationError",
            "message": message,
            "details": {},
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    """
    Handler para erros do SQLAlchemy.
    """
    logger.error(
        "Database error",
        exception_type=exc.__class__.__name__,
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "DatabaseError",
            "message": "Erro ao processar operação no banco de dados",
            "details": {},
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handler genérico para exceções não tratadas.
    """
    logger.error(
        "Unhandled exception",
        exception_type=exc.__class__.__name__,
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "Erro interno do servidor",
            "details": {},
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registra todos os handlers de exceção na aplicação FastAPI.
    """
    app.add_exception_handler(DemeterException, demeter_exception_handler)

    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    app.add_exception_handler(JWTError, jwt_exception_handler)
    app.add_exception_handler(ExpiredSignatureError, jwt_exception_handler)

    app.add_exception_handler(SQLAlchemyError, database_exception_handler)

    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered successfully")
