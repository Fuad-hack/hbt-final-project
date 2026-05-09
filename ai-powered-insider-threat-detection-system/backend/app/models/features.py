"""
Feature Models (Async SQLAlchemy 2.0)
"""

import uuid
from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Boolean, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BehavioralFeature(Base):
    """Behavioral features"""
    __tablename__ = "behavioral_features"
    __table_args__ = {"schema": "threat_detection"}
    
    feature_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    calculation_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    mean_login_hour: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    mean_logout_hour: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    files_per_day: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    usb_per_day: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    emails_per_day: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    out_of_session_access: Mapped[Optional[int]] = mapped_column(Integer)


class GraphFeature(Base):
    """Graph features"""
    __tablename__ = "graph_features"
    __table_args__ = {"schema": "threat_detection"}
    
    graph_feature_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    calculation_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    degree_centrality: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    betweenness_centrality: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))


class NLPEmailFeature(Base):
    """NLP email features"""
    __tablename__ = "nlp_email_features"
    __table_args__ = {"schema": "threat_detection"}
    
    nlp_feature_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("threat_detection.email_logs.email_id", ondelete="CASCADE"), nullable=True)
    sender_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    keyword_flag: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    suspicious_keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    keyword_count: Mapped[int] = mapped_column(Integer, default=0)
    subject_len: Mapped[int] = mapped_column(Integer)
    body_len: Mapped[int] = mapped_column(Integer)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class MergedFeature(Base):
    """Merged features"""
    __tablename__ = "merged_features"
    __table_args__ = {"schema": "threat_detection"}
    
    merged_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    calculation_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    mean_login_hour: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))
    files_per_day: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    degree_centrality: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    is_red_team: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
