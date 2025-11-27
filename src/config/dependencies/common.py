"""
Dependencies comuns para rotas do FastAPI.
"""

from typing import Annotated, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose.exceptions import ExpiredSignatureError, JWTError

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.security.auth import verify_token
from src.config.db.dependencies import get_db

security = HTTPBearer()


async def get_current_user_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> Dict[str, Any]:
    """
    Extrai e valida o token JWT, retornando o payload completo.
    """
    token = credentials.credentials

    try:
        payload = verify_token(token, token_type="access")
        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Por favor, faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    payload: Annotated[Dict[str, Any], Depends(get_current_user_payload)]
) -> int:
    """
    Extrai o ID do usuário autenticado do token JWT.
    """
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém ID de usuário",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID de usuário inválido no token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    payload: Annotated[Dict[str, Any], Depends(get_current_user_payload)]
) -> Dict[str, Any]:
    """
    Retorna as informações do usuário autenticado extraídas do token.
    """
    return payload


async def get_current_active_user(
    current_user: Annotated[Dict[str, Any], Depends(get_current_user)]
) -> Dict[str, Any]:
    """
    Retorna o usuário autenticado e verifica se está ativo.
    """
    return current_user


async def get_refresh_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> Dict[str, Any]:
    """
    Valida e extrai o payload de um refresh token.
    """
    token = credentials.credentials

    try:
        payload = verify_token(token, token_type="refresh")
        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expirado. Por favor, faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Refresh token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_with_permissions(
    payload: Annotated[Dict[str, Any], Depends(get_current_user_payload)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Dict[str, Any]:
    """Carrega usuário com roles e permissions do banco."""

    from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepositoryImpl(db)
    user = await user_repo.get_by_id_with_roles(int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário deletado",
        )

    permissions = set()
    roles = []

    for user_role in user.user_roles:
        roles.append(user_role.role.name)
        for role_permission in user_role.role.role_permissions:
            permissions.add(role_permission.permission.name)

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "roles": roles,
        "permissions": list(permissions),
        "is_admin": "admin" in roles
    }



def require_permission(permission: str):
    """Factory que retorna dependency para verificar permissão específica."""
    async def permission_checker(
        user: Annotated[Dict[str, Any], Depends(get_current_user_with_permissions)]
    ) -> Dict[str, Any]:
        if permission not in user["permissions"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {permission}"
            )
        return user

    return permission_checker


def require_role(role: str):
    """Factory que retorna dependency para verificar role específica."""
    async def role_checker(
        user: Annotated[Dict[str, Any], Depends(get_current_user_with_permissions)]
    ) -> Dict[str, Any]:
        if role not in user["roles"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role necessária: {role}"
            )
        return user

    return role_checker


require_admin = require_role("admin")
require_classificador = require_role("classificador")

CurrentUser = Annotated[Dict[str, Any], Depends(get_current_user)]
CurrentUserId = Annotated[int, Depends(get_current_user_id)]
CurrentActiveUser = Annotated[Dict[str, Any], Depends(get_current_active_user)]
CurrentUserWithPermissions = Annotated[Dict[str, Any], Depends(get_current_user_with_permissions)]
