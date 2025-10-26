"""
Dependencies comuns do FastAPI.
"""

from src.config.dependencies.common import (
    get_current_user,
    get_current_active_user,
    get_current_user_id,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_user_id",
]
