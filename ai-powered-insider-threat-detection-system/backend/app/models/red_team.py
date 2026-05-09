"""
Red Team Models (Async SQLAlchemy 2.0)
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RedTeamFlag(Base):
    """Red team flags"""
    __tablename__ = "red_team_flags"
    __table_args__ = {"schema": "threat_detection"}
    
    flag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    injected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    exercise_name: Mapped[Optional[str]] = mapped_column(String(100))
    injected_behavior: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    was_detected: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    detection_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
