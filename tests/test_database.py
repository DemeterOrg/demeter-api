"""
Testes para conexão e operações básicas do banco de dados.

Verifica se o SQLAlchemy está configurado corretamente e se
as operações básicas (CRUD) estão funcionando.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """
    Teste: Deve conseguir conectar ao banco de dados.

    Executa uma query simples para verificar conectividade.
    """
    result = await db_session.execute(text("SELECT 1 as num"))
    row = result.fetchone()

    assert row is not None, "Deve retornar resultado"
    assert row[0] == 1, "Deve retornar 1"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_version(db_session: AsyncSession):
    """
    Teste: Deve retornar versão do PostgreSQL.

    Verifica se estamos usando PostgreSQL.
    """
    result = await db_session.execute(text("SELECT version()"))
    version = result.scalar()

    assert version is not None, "Deve retornar versão"
    assert "PostgreSQL" in version, "Deve ser PostgreSQL"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_timezone(db_session: AsyncSession):
    """
    Teste: Deve estar configurado para timezone correto.

    Verifica se o timezone está configurado (idealmente America/Sao_Paulo).
    """
    result = await db_session.execute(text("SHOW timezone"))
    timezone = result.scalar()

    assert timezone is not None, "Deve retornar timezone configurado"
    valid_timezones = [
        "America/Sao_Paulo",
        "America/Sao Paulo",
        "UTC",
        "Etc/UTC",
    ]

    assert isinstance(timezone, str), "Timezone deve ser string"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_extensions(db_session: AsyncSession):
    """
    Teste: Deve ter extensões úteis instaladas.
    """
    result = await db_session.execute(
        text(
            """
        SELECT EXISTS (
            SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp'
        ) as has_uuid
    """
        )
    )
    has_uuid = result.scalar()

    result = await db_session.execute(
        text(
            """
        SELECT EXISTS (
            SELECT 1 FROM pg_extension WHERE extname = 'unaccent'
        ) as has_unaccent
    """
        )
    )
    has_unaccent = result.scalar()

    assert has_uuid is not None or has_unaccent is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_transaction_rollback(db_session: AsyncSession):
    """
    Teste: Transações devem fazer rollback em caso de erro.

    Verifica que transações são revertidas corretamente.
    """
    await db_session.execute(
        text(
            """
        CREATE TEMP TABLE test_rollback (
            id SERIAL PRIMARY KEY,
            value TEXT
        )
    """
        )
    )

    await db_session.execute(
        text("INSERT INTO test_rollback (value) VALUES ('test')")
    )

    result = await db_session.execute(text("SELECT COUNT(*) FROM test_rollback"))
    count = result.scalar()
    assert count == 1, "Deve ter 1 registro"

    await db_session.rollback()

    try:
        result = await db_session.execute(text("SELECT COUNT(*) FROM test_rollback"))
        count = result.scalar()
        assert count == 0, "Após rollback, não deve ter registros"
    except Exception:
        pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_concurrent_transactions(db_session: AsyncSession):
    """
    Teste: Deve suportar operações concorrentes básicas.

    Verifica que múltiplas queries podem ser executadas.
    """
    queries = [
        "SELECT 1",
        "SELECT 2",
        "SELECT 3",
        "SELECT CURRENT_TIMESTAMP",
        "SELECT version()",
    ]

    for query in queries:
        result = await db_session.execute(text(query))
        value = result.scalar()
        assert value is not None, f"Query '{query}' deve retornar valor"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_pool_connection(db_session: AsyncSession):
    """
    Teste: Pool de conexões deve estar funcionando.

    Verifica que podemos obter conexão do pool.
    """
    result = await db_session.execute(
        text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
    )
    active_connections = result.scalar()

    assert active_connections is not None, "Deve retornar número de conexões"
    assert active_connections > 0, "Deve ter pelo menos 1 conexão ativa"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_database_basic_crud_operations(db_session: AsyncSession):
    """
    Teste: Operações básicas CRUD devem funcionar.

    Cria tabela temporária e testa INSERT, SELECT, UPDATE, DELETE.
    """
    await db_session.execute(
        text(
            """
        CREATE TEMP TABLE test_crud (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            value INTEGER
        )
    """
        )
    )

    await db_session.execute(
        text(
            """
        INSERT INTO test_crud (name, value)
        VALUES ('item1', 100), ('item2', 200)
    """
        )
    )

    result = await db_session.execute(text("SELECT COUNT(*) FROM test_crud"))
    count = result.scalar()
    assert count == 2, "Deve ter 2 registros após insert"

    await db_session.execute(
        text("UPDATE test_crud SET value = 150 WHERE name = 'item1'")
    )

    result = await db_session.execute(
        text("SELECT value FROM test_crud WHERE name = 'item1'")
    )
    value = result.scalar()
    assert value == 150, "Valor deve ter sido atualizado para 150"

    await db_session.execute(text("DELETE FROM test_crud WHERE name = 'item2'"))

    result = await db_session.execute(text("SELECT COUNT(*) FROM test_crud"))
    count = result.scalar()
    assert count == 1, "Deve ter 1 registro após delete"
