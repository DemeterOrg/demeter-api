from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.config.settings import settings

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class Base(DeclarativeBase):
    """
    Classe base para todos os modelos SQLAlchemy.
    """
    metadata = metadata

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Gera nome de tabela automaticamente baseado no nome da classe.
        """
        return cls.__name__.lower() + "s"


class DatabaseEngine:
    """
    Gerenciador do engine e sessões do banco de dados.
    """
    def __init__(self) -> None:
        """Inicializa o engine e session factory com base nas configurações"""
        self._engine: AsyncEngine = create_async_engine(
            url=settings.database_url_str,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
        )

        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        """Retorna o engine assíncrono"""
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Retorna a factory de sessões"""
        return self._session_factory

    async def create_tables(self) -> None:
        """
        Cria todas as tabelas no banco de dados.
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    async def drop_tables(self) -> None:
        """
        Remove todas as tabelas do banco de dados.
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self) -> None:
        """Fecha o engine e todas as conexões"""
        await self._engine.dispose()

database = DatabaseEngine()
async_session_maker = database.session_factory
