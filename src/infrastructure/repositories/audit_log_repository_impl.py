"""Implementação do repositório de Audit Logs."""

from typing import Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models.audit_log import AuditLog
from src.config.exceptions.custom_exceptions import DatabaseError
from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class AuditLogRepositoryImpl:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        changes: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Cria um novo log de auditoria."""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                changes=changes,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.session.add(audit_log)
            await self.session.flush()
            await self.session.refresh(audit_log)

            logger.info(
                "Audit log created",
                audit_log_id=audit_log.id,
                action=action,
                resource=f"{resource_type}:{resource_id}"
            )
            return audit_log
        except Exception as e:
            await self.session.rollback()
            logger.error("Error creating audit log", action=action, error=str(e))
            raise DatabaseError(f"Erro ao criar log de auditoria: {str(e)}")

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[AuditLog]:
        """Lista logs de auditoria com filtros opcionais."""
        try:
            conditions = []

            if user_id is not None:
                conditions.append(AuditLog.user_id == user_id)

            if action:
                conditions.append(AuditLog.action == action)

            if resource_type:
                conditions.append(AuditLog.resource_type == resource_type)

            if start_date:
                conditions.append(AuditLog.created_at >= start_date)

            if end_date:
                conditions.append(AuditLog.created_at <= end_date)

            stmt = select(AuditLog)
            if conditions:
                stmt = stmt.where(and_(*conditions))

            stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)

            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error listing audit logs", error=str(e))
            raise DatabaseError(f"Erro ao listar logs de auditoria: {str(e)}")

    async def get_by_resource(
        self,
        resource_type: str,
        resource_id: int,
        limit: int = 50
    ) -> list[AuditLog]:
        """Busca logs de auditoria para um recurso específico."""
        try:
            stmt = (
                select(AuditLog)
                .where(
                    AuditLog.resource_type == resource_type,
                    AuditLog.resource_id == resource_id
                )
                .order_by(AuditLog.created_at.desc())
                .limit(limit)
            )

            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error("Error fetching audit logs by resource", resource=f"{resource_type}:{resource_id}", error=str(e))
            raise DatabaseError(f"Erro ao buscar logs: {str(e)}")
