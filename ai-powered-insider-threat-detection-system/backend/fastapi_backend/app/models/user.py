"""
User Model - Core reference table for all user-related data
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class User(Base):
    """Master table for all system users"""
    
    __tablename__ = "users"
    
    # Using UUID for exposed API entities
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    department: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    login_sessions: Mapped[List["LoginSession"]] = relationship(
        "LoginSession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    file_access_logs: Mapped[List["FileAccessLog"]] = relationship(
        "FileAccessLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    usb_usage_logs: Mapped[List["USBUsageLog"]] = relationship(
        "USBUsageLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    sent_emails: Mapped[List["EmailLog"]] = relationship(
        "EmailLog",
        back_populates="sender",
        foreign_keys="EmailLog.sender_user_id",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    behavioral_features: Mapped[List["BehavioralFeature"]] = relationship(
        "BehavioralFeature",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    graph_features: Mapped[List["GraphFeature"]] = relationship(
        "GraphFeature",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    merged_features: Mapped[List["MergedFeature"]] = relationship(
        "MergedFeature",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    anomaly_scores: Mapped[List["AnomalyScore"]] = relationship(
        "AnomalyScore",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    xai_explanations: Mapped[List["XAIExplanation"]] = relationship(
        "XAIExplanation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    red_team_flags: Mapped[List["RedTeamFlag"]] = relationship(
        "RedTeamFlag",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<User {self.username}>"
