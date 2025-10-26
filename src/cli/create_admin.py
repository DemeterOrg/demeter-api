"""
Comando CLI para criar usuário admin.
"""

import argparse
import asyncio
from datetime import datetime, timezone

from src.config.db.database import async_session_maker
from src.config.security.password import get_password_hash
from src.infrastructure.models.user import User
from src.infrastructure.repositories.role_repository_impl import RoleRepositoryImpl
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


async def create_admin(email: str, name: str, password: str, phone: str):
    """Cria usuário admin no sistema."""
    async with async_session_maker() as db:
        try:
            from sqlalchemy import select
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Erro: Email '{email}' já cadastrado")
                logger.warning(f"Admin creation failed: email already exists", email=email)
                return

            hashed_password = get_password_hash(password)
            user = User(
                email=email,
                name=name,
                phone=phone,
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True,
            )

            db.add(user)
            await db.flush()
            await db.refresh(user)

            role_repo = RoleRepositoryImpl(db)
            admin_role = await role_repo.get_by_name("admin")

            if not admin_role:
                print("Erro: Role 'admin' não encontrada no banco")
                logger.error("Admin creation failed: admin role not found")
                await db.rollback()
                return

            await role_repo.assign_role_to_user(
                user_id=user.id,
                role_id=admin_role.id,
                assigned_by=None
            )

            await db.commit()

            print(" Admin criado com sucesso!")
            print(f"   Email: {email}")
            print(f"   Nome: {name}")
            print(f"   ID: {user.id}")

            logger.info(f"Admin user created successfully", user_id=user.id, email=email)

        except Exception as e:
            await db.rollback()
            print(f"Erro ao criar admin: {str(e)}")
            logger.error(f"Admin creation failed", error=str(e), exc_info=True)


def main():
    """Entry point do comando CLI."""
    parser = argparse.ArgumentParser(description="Criar usuário admin no sistema")
    parser.add_argument("--email", required=True, help="Email do admin")
    parser.add_argument("--name", required=True, help="Nome do admin")
    parser.add_argument("--password", required=True, help="Senha do admin")
    parser.add_argument("--phone", required=True, help="Telefone do admin")

    args = parser.parse_args()

    asyncio.run(create_admin(
        email=args.email,
        name=args.name,
        password=args.password,
        phone=args.phone
    ))


if __name__ == "__main__":
    main()
