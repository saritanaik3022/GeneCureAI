"""
API dependencies and shared utilities.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

__all__ = ["get_db"]
