"""
XAI Models (Async SQLAlchemy 2.0)
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class XAIExplanation(Base):
    """XAI explanations"""
    __tablename__ = "xai_explanations"
    __table_args__ = {"schema": "threat_detection"}
    
    explanation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    score_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threat_detection.anomaly_scores.score_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("threat_detection.users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    explanation_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    shap_feature_importance: Mapped[Optional[dict]] = mapped_column(JSONB)
    lime_explanations: Mapped[Optional[list]] = mapped_column(JSONB)
    top_feature_1: Mapped[Optional[str]] = mapped_column(String(50))
    top_feature_1_weight: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
