"""Schemas Pydantic para Classifications."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ClassificationResponse(BaseModel):
    """Response de uma classificação."""

    id: int
    user_id: int
    grain_type: str
    confidence_score: Decimal
    image_path: str
    extra_data: dict | None = None
    notes: str | None = None
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClassificationUpdate(BaseModel):
    """Update de classificação (apenas notes)."""

    notes: Optional[str] = Field(None, max_length=500)


class ClassificationListResponse(BaseModel):
    """Lista paginada de classificações."""

    items: list[ClassificationResponse]
    total: int
    skip: int
    limit: int
