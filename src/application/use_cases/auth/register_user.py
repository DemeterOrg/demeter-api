"""Use Case para registro de novos usuários."""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.user_repository import UserRepository
from src.domain.entities.user import UserEntity
from src.application.schemas.user import UserCreate, UserResponse
from src.config.security.password import get_password_hash
from src.config.exceptions.custom_exceptions import ConflictError, DatabaseError
from src.config.logging.logger import get_logger
from src.infrastructure.repositories.role_repository_impl import RoleRepositoryImpl

logger = get_logger(__name__)


class RegisterUserUseCase:
    """Registra novos usuários e atribui role 'classificador' automaticamente."""

    def __init__(self, user_repository: UserRepository, db: AsyncSession):
        self.user_repository = user_repository
        self.db = db

    async def execute(self, user_data: UserCreate) -> UserResponse:
        """
        Executa o registro de um novo usuário.
        """
        logger.info("Starting user registration", email=user_data.email)

        existing_user = await self.user_repository.exists_by_email(user_data.email)
        if existing_user:
            logger.warning("Registration failed - email already exists", email=user_data.email)
            raise ConflictError(
                f"Email '{user_data.email}' já está cadastrado",
                details={"email": user_data.email},
            )

        hashed_password = get_password_hash(user_data.password)

        user_entity = UserEntity(
            email=user_data.email,
            name=user_data.name,
            phone=user_data.phone,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
        )

        created_user = await self.user_repository.create(user_entity)
        role_repo = RoleRepositoryImpl(self.db)
        classificador_role = await role_repo.get_by_name("classificador")

        if not classificador_role:
            logger.error("Role 'classificador' not found in database")
            raise DatabaseError("Erro de configuração: role 'classificador' não encontrada")

        await role_repo.assign_role_to_user(
            user_id=created_user.id,
            role_id=classificador_role.id,
            assigned_by=None
        )

        logger.info(
            "User registered successfully",
            user_id=created_user.id,
            email=created_user.email,
            role="classificador"
        )

        return UserResponse(
            id=created_user.id,
            email=created_user.email,
            name=created_user.name,
            phone=created_user.phone,
            is_active=created_user.is_active,
            is_verified=created_user.is_verified,
            created_at=created_user.created_at or datetime.now(timezone.utc),
            last_login=created_user.last_login,
        )
