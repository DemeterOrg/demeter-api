"""
Health check endpoint.

Verifica o status da API e suas dependências de forma detalhada.
"""

import os
import shutil
import time
from typing import Any

from fastapi import APIRouter, status
from sqlalchemy import text

from src.config.db.dependencies import DbSessionDep

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check completo",
    description="Verifica o status da API e suas dependências (banco, disco, etc)",
)
async def health_check(db: DbSessionDep) -> dict[str, Any]:
    """
    Verifica o status da API e suas dependências.

    Retorna:
    - **status**: Status geral (ok | degraded | unhealthy)
    - **version**: Versão da API
    - **environment**: Ambiente de execução
    - **checks**: Detalhes de cada verificação
      - **database**: Status e latência do PostgreSQL
      - **disk**: Espaço disponível em disco
    """
    health_status = {
        "status": "ok",
        "version": os.getenv("VERSION", "1.0.0"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "checks": {},
    }
    try:
        start = time.time()
        await db.execute(text("SELECT 1"))
        latency = round((time.time() - start) * 1000, 2)  # ms

        health_status["checks"]["database"] = {
            "status": "healthy",
            "latency_ms": latency,
        }

        if latency > 100:
            health_status["status"] = "degraded"
            health_status["checks"]["database"]["warning"] = "High latency"

    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }

    try:
        upload_dir = os.getenv("UPLOAD_DIR", "uploads")

        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)

        total, used, free = shutil.disk_usage(upload_dir)
        free_gb = round(free / (1024**3), 2)

        if free_gb > 1:
            disk_status = "healthy"
        elif free_gb > 0.5:
            disk_status = "degraded"
            health_status["status"] = "degraded"
        else:
            disk_status = "unhealthy"
            health_status["status"] = "unhealthy"

        health_status["checks"]["disk"] = {
            "status": disk_status,
            "free_gb": free_gb,
            "total_gb": round(total / (1024**3), 2),
        }

    except Exception as e:
        health_status["checks"]["disk"] = {
            "status": "unknown",
            "error": str(e),
        }

    try:
        upload_dir = os.getenv("UPLOAD_DIR", "uploads")

        if os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK):
            health_status["checks"]["uploads"] = {
                "status": "healthy",
                "path": upload_dir,
                "writable": True,
            }
        else:
            health_status["checks"]["uploads"] = {
                "status": "degraded",
                "path": upload_dir,
                "writable": False,
            }
            if health_status["status"] == "ok":
                health_status["status"] = "degraded"

    except Exception as e:
        health_status["checks"]["uploads"] = {
            "status": "unknown",
            "error": str(e),
        }

    return health_status
