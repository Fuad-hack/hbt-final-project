"""
XAI (Explainable AI) Models - SHAP and LIME explanations
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class XAIExplanation(Base):
    """SHAP and LIME explainability results for high-risk users"""
    
    __tablename__ = "xai_explanations"
    
    explanation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    score_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("anomaly_scores.score_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    explanation_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )  # SHAP, LIME, LIME_LOCAL
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    
    # SHAP global feature importance
    shap_feature_importance: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # LIME local explanation
    lime_explanations: Mapped[Optional[list]] = mapped_column(JSONB)
    
    # Top contributing features (pre-calculated for quick access)
    top_feature_1: Mapped[Optional[str]] = mapped_column(String(50))
    top_feature_1_weight: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    top_feature_2: Mapped[Optional[str]] = mapped_column(String(50))
    top_feature_2_weight: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    top_feature_3: Mapped[Optional[str]] = mapped_column(String(50))
    top_feature_3_weight: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    
    explanation_summary: Mapped[Optional[str]] = mapped_column(String(2000))
    
    # Relationships
    anomaly_score: Mapped["AnomalyScore"] = relationship(
        "AnomalyScore",
        back_populates="xai_explanations"
    )
    user: Mapped["User"] = relationship("User", back_populates="xai_explanations")
