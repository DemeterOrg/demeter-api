"""
Configuração global para testes pytest.

Este arquivo é carregado automaticamente pelo pytest e define
fixtures e configurações compartilhadas entre todos os testes.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config.db.database import Base, get_db
from src.main import app

# ==============================================================================
# Configuração de Ambiente para Testes
# ==============================================================================

# Forçar ambiente de teste
os.environ["ENVIRONMENT"] = "test"

# URL do banco de testes (pode ser sobrescrito por variável de ambiente)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://demeter:demeter_dev_password@localhost:5432/demeter_test_db",
)


# ==============================================================================
# Event Loop Fixture (para testes assíncronos)
# ==============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Cria event loop para toda sessão de testes.
    Necessário para testes assíncronos funcionarem corretamente.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==============================================================================
# Database Fixtures
# ==============================================================================


@pytest.fixture(scope="session")
async def test_engine():
    """
    Cria engine de banco de dados para testes.
    Scope: session (criado uma vez para todos os testes).
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,  # Não mostrar SQL logs em testes
        pool_pre_ping=True,
    )

    # Criar todas as tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: dropar todas as tabelas após os testes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(
    test_engine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Cria sessão de banco de dados para cada teste.
    Scope: function (nova sessão para cada teste).

    Usa transação que é revertida ao final do teste,
    mantendo o banco limpo entre testes.
    """
    # Criar sessão
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        # Iniciar transação
        async with session.begin():
            yield session
            # Rollback automático ao final do teste
            await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Cria cliente HTTP de teste para a API.
    Scope: function (novo cliente para cada teste).

    Sobrescreve a dependência get_db para usar a sessão de teste.
    """

    # Sobrescrever dependência de DB
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Criar cliente
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    # Limpar overrides
    app.dependency_overrides.clear()


# ==============================================================================
# Helper Fixtures
# ==============================================================================


@pytest.fixture
def sample_user_data() -> dict:
    """
    Dados de exemplo para criar usuário.
    """
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Test123!@#",
        "phone": "11999999999",
    }


@pytest.fixture
def sample_admin_data() -> dict:
    """
    Dados de exemplo para criar admin.
    """
    return {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "Admin123!@#",
        "phone": "11988888888",
    }


# ==============================================================================
# Markers Configurados
# ==============================================================================

# pytest -m unit          # Apenas testes unitários
# pytest -m integration   # Apenas testes de integração
# pytest -m slow          # Apenas testes lentos
# pytest -m smoke         # Apenas smoke tests
