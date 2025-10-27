"""
API REST versão 1.

Agrupa todos os routers da versão 1 da API.
"""

from fastapi import APIRouter

from src.presentation.api.v1.auth.router import router as auth_router
from src.presentation.api.v1.users.router import router as users_router
from src.presentation.api.v1.classifications.router import router as classifications_router
from src.presentation.api.v1.admin.classifications import router as admin_classifications_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(classifications_router, tags=["Classifications"])
router.include_router(admin_classifications_router, tags=["Admin - Classifications"])

__all__ = ["router"]
