"""
Entry point da aplicação DEMETER API.

Esta é a aplicação principal FastAPI que configura todos os routers,
middleware, exception handlers e inicializações necessárias.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.config.logging.logger import logger
from src.config.exceptions.handlers import register_exception_handlers
from src.config.db.database import database
from src.presentation.api.v1 import router as v1_router
from src.presentation.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager da aplicação.

    Executa código de inicialização e finalização.
    """
    # Startup
    logger.info(
        "Starting DEMETER API",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Aqui você pode adicionar inicializações necessárias
    # Por exemplo: criar tabelas, executar migrations, etc.

    yield

    # Shutdown
    logger.info("Shutting down DEMETER API")

    # Fechar conexões
    await database.close()


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Registrar exception handlers
register_exception_handlers(app)

# Incluir routers
app.include_router(health_router)
app.include_router(v1_router)


@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raiz da API.

    Retorna informações básicas sobre a API.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs" if settings.is_development else "disabled in production",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
