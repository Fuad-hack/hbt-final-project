"""
Raw Log Models - Login sessions, file access, USB usage, emails
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LoginSession(Base):
    """Daily login/logout session records"""
    
    __tablename__ = "login_sessions"
    
    session_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    login_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    logout_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    session_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="login_sessions")
    
    __table_args__ = (
        # Ensure logout is after login
        CheckConstraint(
            "logout_time IS NULL OR logout_time > login_time",
            name="valid_session"
        ),
    )


class FileAccessLog(Base):
    """User file access events"""
    
    __tablename__ = "file_access_logs"
    
    access_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    access_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    operation_type: Mapped[str] = mapped_column(String(20), default="read")
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="file_access_logs")


class USBUsageLog(Base):
    """USB device connection/disconnection tracking"""
    
    __tablename__ = "usb_usage_logs"
    
    usb_event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    device_id: Mapped[str] = mapped_column(String(100), nullable=False)
    plug_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    unplug_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    device_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="usb_usage_logs")
    
    __table_args__ = (
        CheckConstraint(
            "unplug_time IS NULL OR unplug_time > plug_time",
            name="valid_usb_usage"
        ),
    )


class EmailLog(Base):
    """Email communication records"""
    
    __tablename__ = "email_logs"
    
    email_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sender_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sender_email: Mapped[str] = mapped_column(String(100), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(100), nullable=False)
    sent_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    subject: Mapped[Optional[str]] = mapped_column(String(500))
    body_text: Mapped[Optional[str]] = mapped_column(Text)
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False)
    attachment_count: Mapped[int] = mapped_column(Integer, default=0)
    is_external: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Relationship
    sender: Mapped["User"] = relationship("User", back_populates="sent_emails")
    
    # Self-referential for replies (optional)
    parent_email_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("email_logs.email_id"),
        nullable=True
    )
