"""
Log Models - Raw log tables (Async SQLAlchemy 2.0)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LoginSession(Base):
    """Login/logout session records"""
    __tablename__ = "login_sessions"
    __table_args__ = {"schema": "threat_detection"}
    
    session_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    login_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    logout_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    session_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)


class FileAccessLog(Base):
    """File access events"""
    __tablename__ = "file_access_logs"
    __table_args__ = {"schema": "threat_detection"}
    
    access_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    access_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    operation_type: Mapped[str] = mapped_column(String(20), default="read")


class USBUsageLog(Base):
    """USB usage logs"""
    __tablename__ = "usb_usage_logs"
    __table_args__ = {"schema": "threat_detection"}
    
    usb_event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    device_id: Mapped[str] = mapped_column(String(100), nullable=False)
    plug_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    unplug_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    device_name: Mapped[Optional[str]] = mapped_column(String(255))


class EmailLog(Base):
    """Email logs"""
    __tablename__ = "email_logs"
    __table_args__ = {"schema": "threat_detection"}
    
    email_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sender_user_id: Mapped[int] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    sender_email: Mapped[str] = mapped_column(String(100), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(100), nullable=False)
    sent_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    subject: Mapped[Optional[str]] = mapped_column(String(500))
    body_text: Mapped[Optional[str]] = mapped_column(Text)
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False)
    attachment_count: Mapped[int] = mapped_column(Integer, default=0)
    is_external: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
