"""
Machine Learning Models - Model Runs and Anomaly Scores
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Boolean, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ModelRun(Base):
    """Training session metadata and model performance metrics"""
    
    __tablename__ = "model_runs"
    
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    run_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    run_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        index=True
    )
    training_date_start: Mapped[date] = mapped_column(Date, nullable=False)
    training_date_end: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Model hyperparameters
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Performance metrics
    training_samples: Mapped[Optional[int]] = mapped_column(Integer)
    contamination_rate: Mapped[Optional[float]] = mapped_column(Numeric(4, 3))
    precision_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    recall_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    f1_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    model_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Relationships
    anomaly_scores: Mapped[list["AnomalyScore"]] = relationship(
        "AnomalyScore",
        back_populates="model_run",
        lazy="selectin"
    )


class AnomalyScore(Base):
    """Anomaly detection scores from 3 ML models per user"""
    
    __tablename__ = "anomaly_scores"
    
    score_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("model_runs.run_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    calculation_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    
    # Individual model scores
    isolation_forest_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4)
    )
    oneclass_svm_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    autoencoder_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    
    # Combined score
    composite_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 4),
        index=True
    )
    
    # Classification
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    risk_level: Mapped[Optional[str]] = mapped_column(
        String(20),
        index=True
    )  # low, medium, high, critical
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="anomaly_scores")
    model_run: Mapped["ModelRun"] = relationship("ModelRun", back_populates="anomaly_scores")
    xai_explanations: Mapped[list["XAIExplanation"]] = relationship(
        "XAIExplanation",
        back_populates="anomaly_score",
        lazy="selectin"
    )
    
    __table_args__ = (
        UniqueConstraint("user_id", "run_id", name="uq_anomaly_user_run"),
    )
