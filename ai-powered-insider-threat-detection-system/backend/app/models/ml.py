"""
ML Models (Async SQLAlchemy 2.0)
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Integer, Numeric, Date, DateTime, ForeignKey, Boolean, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ModelRun(Base):
    """Model runs"""
    __tablename__ = "model_runs"
    __table_args__ = {"schema": "threat_detection"}
    
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    run_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    hyperparameters: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class AnomalyScore(Base):
    """Anomaly scores"""
    __tablename__ = "anomaly_scores"
    __table_args__ = {"schema": "threat_detection"}
    
    score_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threat_detection.model_runs.run_id", ondelete="CASCADE"), nullable=False, index=True)
    calculation_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    isolation_forest_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    oneclass_svm_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    autoencoder_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    composite_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), index=True)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), index=True)
