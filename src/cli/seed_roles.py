"""
Comando CLI para popular roles e permissions iniciais.
"""

import asyncio

from src.config.db.database import async_session_maker
from src.infrastructure.models.role import Role
from src.infrastructure.models.permission import Permission
from src.infrastructure.models.role_permission import RolePermission
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


async def seed_roles_and_permissions():
    """Popula roles e permissions iniciais no banco."""
    async with async_session_maker() as db:
        try:
            # Verificar se já existem roles
            from sqlalchemy import select
            result = await db.execute(select(Role))
            existing_roles = result.scalars().all()

            if existing_roles:
                print("⚠ Roles já existem no banco. Pulando seed.")
                logger.info("Seed skipped: roles already exist")
                return

            # Criar roles
            print("📝 Criando roles...")
            classificador_role = Role(
                name="classificador",
                description="Usuário classificador",
                is_system=True
            )
            admin_role = Role(
                name="admin",
                description="Administrador do sistema",
                is_system=True
            )

            db.add_all([classificador_role, admin_role])
            await db.flush()

            print(f"   ✓ Role 'classificador' criada (ID: {classificador_role.id})")
            print(f"   ✓ Role 'admin' criada (ID: {admin_role.id})")

            # Criar permissions
            print("\n📝 Criando permissions...")
            permissions = [
                Permission(
                    name="classifications:create:own",
                    resource="classifications",
                    action="create",
                    scope="own",
                    description="Criar suas próprias classificações"
                ),
                Permission(
                    name="classifications:read:own",
                    resource="classifications",
                    action="read",
                    scope="own",
                    description="Visualizar suas próprias classificações"
                ),
                Permission(
                    name="classifications:update:own",
                    resource="classifications",
                    action="update",
                    scope="own",
                    description="Atualizar suas próprias classificações"
                ),
                Permission(
                    name="classifications:delete:own",
                    resource="classifications",
                    action="delete",
                    scope="own",
                    description="Deletar suas próprias classificações"
                ),
                Permission(
                    name="classifications:read:all",
                    resource="classifications",
                    action="read",
                    scope="all",
                    description="Visualizar todas as classificações"
                ),
                Permission(
                    name="classifications:delete:all",
                    resource="classifications",
                    action="delete",
                    scope="all",
                    description="Deletar qualquer classificação"
                ),
            ]

            db.add_all(permissions)
            await db.flush()

            for perm in permissions:
                print(f"   ✓ Permission '{perm.name}' criada (ID: {perm.id})")

            # Associar permissions às roles
            print("\n📝 Associando permissions às roles...")

            # Classificador: apenas permissões :own
            for perm in permissions[:4]:
                role_perm = RolePermission(
                    role_id=classificador_role.id,
                    permission_id=perm.id
                )
                db.add(role_perm)
            print(f"   ✓ 4 permissions associadas à role 'classificador'")

            # Admin: todas as permissões
            for perm in permissions:
                role_perm = RolePermission(
                    role_id=admin_role.id,
                    permission_id=perm.id
                )
                db.add(role_perm)
            print(f"   ✓ {len(permissions)} permissions associadas à role 'admin'")

            await db.commit()

            print("\n✅ Seed concluído com sucesso!")
            logger.info(
                "Roles and permissions seeded successfully",
                roles_created=2,
                permissions_created=len(permissions)
            )

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Erro ao popular banco: {str(e)}")
            logger.error("Seed failed", error=str(e), exc_info=True)
            raise


def main():
    """Entry point do comando CLI."""
    asyncio.run(seed_roles_and_permissions())


if __name__ == "__main__":
    main()
