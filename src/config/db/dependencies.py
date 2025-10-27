from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.db.database import database


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """ dependecia que fornece uma sessão do banco de dados para as rotas do FastAPI"""
    async with database.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """ context manager assícrono para acesso ao banco fora de routers """
    async with database.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()