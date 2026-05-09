"""
Feature Engineering Models - Behavioral, Graph, NLP, and Merged Features
"""

import uuid
from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Boolean, func, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BehavioralFeature(Base):
    """Engineered behavioral features from raw logs"""
    
    __tablename__ = "behavioral_features"
    
    feature_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    calculation_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    
    # Login/Logout patterns
    mean_login_hour: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2),
        CheckConstraint("mean_login_hour >= 0 AND mean_login_hour <= 24")
    )
    mean_logout_hour: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2),
        CheckConstraint("mean_logout_hour >= 0 AND mean_logout_hour <= 24")
    )
    std_login_hour: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2),
        CheckConstraint("std_login_hour >= 0")
    )
    
    # Activity rates (per day)
    files_per_day: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2),
        CheckConstraint("files_per_day >= 0")
    )
    usb_per_day: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2),
        CheckConstraint("usb_per_day >= 0")
    )
    emails_per_day: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2),
        CheckConstraint("emails_per_day >= 0")
    )
    
    # Anomaly indicators
    out_of_session_access: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("out_of_session_access >= 0")
    )
    after_hours_logins: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("after_hours_logins >= 0")
    )
    weekend_activity_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("weekend_activity_count >= 0")
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="behavioral_features")
    
    __table_args__ = (
        UniqueConstraint("user_id", "calculation_date", name="uq_behavioral_user_date"),
    )


class GraphFeature(Base):
    """Graph network analysis features"""
    
    __tablename__ = "graph_features"
    
    graph_feature_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    calculation_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    
    # Graph centrality metrics (0-1 range)
    degree_centrality: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        CheckConstraint("degree_centrality >= 0 AND degree_centrality <= 1")
    )
    betweenness_centrality: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        CheckConstraint("betweenness_centrality >= 0 AND betweenness_centrality <= 1")
    )
    closeness_centrality: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        CheckConstraint("closeness_centrality >= 0 AND closeness_centrality <= 1")
    )
    eigenvector_centrality: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        CheckConstraint("eigenvector_centrality >= 0 AND eigenvector_centrality <= 1")
    )
    clustering_coefficient: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        CheckConstraint("clustering_coefficient >= 0 AND clustering_coefficient <= 1")
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="graph_features")
    
    __table_args__ = (
        UniqueConstraint("user_id", "calculation_date", name="uq_graph_user_date"),
    )


class NLPEmailFeature(Base):
    """NLP extracted features from email content"""
    
    __tablename__ = "nlp_email_features"
    
    nlp_feature_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("email_logs.email_id", ondelete="CASCADE"),
        nullable=True
    )
    sender_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Suspicious keyword detection
    keyword_flag: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    suspicious_keywords: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    keyword_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Text features
    subject_len: Mapped[int] = mapped_column(Integer)
    body_len: Mapped[int] = mapped_column(Integer)
    
    # Sentiment analysis
    sentiment_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20))
    urgency_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="nlp_email_features")


class MergedFeature(Base):
    """Consolidated feature set combining all feature types"""
    
    __tablename__ = "merged_features"
    
    merged_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    calculation_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    
    # References to source features (for audit trail)
    behavioral_feature_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("behavioral_features.feature_id"),
        nullable=True
    )
    graph_feature_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("graph_features.graph_feature_id"),
        nullable=True
    )
    
    # Behavioral features (flattened)
    mean_login_hour: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2),
        CheckConstraint("mean_login_hour >= 0 AND mean_login_hour <= 24")
    )
    mean_logout_hour: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2),
        CheckConstraint("mean_logout_hour >= 0 AND mean_logout_hour <= 24")
    )
    files_per_day: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2),
        CheckConstraint("files_per_day >= 0")
    )
    usb_per_day: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2),
        CheckConstraint("usb_per_day >= 0")
    )
    emails_per_day: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2),
        CheckConstraint("emails_per_day >= 0")
    )
    out_of_session_access: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("out_of_session_access >= 0")
    )
    
    # Graph features
    degree_centrality: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        CheckConstraint("degree_centrality >= 0 AND degree_centrality <= 1")
    )
    betweenness_centrality: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        CheckConstraint("betweenness_centrality >= 0 AND betweenness_centrality <= 1")
    )
    
    # NLP aggregated features (by user)
    keyword_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    avg_subject_len: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2),
        CheckConstraint("avg_subject_len >= 0")
    )
    avg_sentiment: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        CheckConstraint("avg_sentiment >= -1 AND avg_sentiment <= 1")
    )
    suspicious_email_ratio: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        CheckConstraint("suspicious_email_ratio >= 0 AND suspicious_email_ratio <= 1")
    )
    
    # Target variable for training
    is_red_team: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="merged_features")
    
    __table_args__ = (
        UniqueConstraint("user_id", "calculation_date", name="uq_merged_user_date"),
    )
