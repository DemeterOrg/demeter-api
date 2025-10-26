"""
Handlers globais de exceções para o FastAPI.

Este módulo define handlers customizados para capturar e tratar exceções
de forma consistente em toda a aplicação, retornando respostas HTTP
padronizadas e logando erros apropriadamente.
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

    Args:
        request: Request do FastAPI
        exc: Exceção DemeterException levantada

    Returns:
        JSONResponse com detalhes do erro
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

    Args:
        request: Request do FastAPI
        exc: Exceção de validação do Pydantic

    Returns:
        JSONResponse com detalhes dos erros de validação
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

    Args:
        request: Request do FastAPI
        exc: Exceção JWT

    Returns:
        JSONResponse com mensagem de erro de autenticação
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

    Args:
        request: Request do FastAPI
        exc: Exceção do SQLAlchemy

    Returns:
        JSONResponse com mensagem de erro de banco de dados
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

    Args:
        request: Request do FastAPI
        exc: Exceção não tratada

    Returns:
        JSONResponse com mensagem genérica de erro interno
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

    Este método deve ser chamado durante a inicialização da aplicação
    para configurar o tratamento global de exceções.

    Args:
        app: Instância do FastAPI

    Example:
        ```python
        from fastapi import FastAPI
        from src.config.exceptions.handlers import register_exception_handlers

        app = FastAPI()
        register_exception_handlers(app)
        ```
    """
    # Exceções customizadas da aplicação
    app.add_exception_handler(DemeterException, demeter_exception_handler)

    # Exceções de validação do Pydantic
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Exceções de JWT
    app.add_exception_handler(JWTError, jwt_exception_handler)
    app.add_exception_handler(ExpiredSignatureError, jwt_exception_handler)

    # Exceções de banco de dados
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)

    # Exceção genérica para erros não tratados
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered successfully")
