"""
Red Team Models - Attack simulation tracking
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RedTeamFlag(Base):
    """Red team attack simulation records with ground truth labels"""
    
    __tablename__ = "red_team_flags"
    
    flag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    injected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    
    # Red team exercise details
    exercise_name: Mapped[Optional[str]] = mapped_column(String(100))
    injected_behavior: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # after_hours_access, mass_download, suspicious_usb
    behavior_description: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Attack simulation parameters
    data_volume_mb: Mapped[Optional[int]] = mapped_column(Integer)
    target_file_count: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Detection tracking
    was_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True
    )
    detection_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    detection_latency_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Reference to merged_features for ground truth
    merged_feature_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("merged_features.merged_id"),
        nullable=True
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="red_team_flags")
    
    __table_args__ = (
        UniqueConstraint("user_id", "injected_behavior", name="uq_redteam_user_behavior"),
    )
