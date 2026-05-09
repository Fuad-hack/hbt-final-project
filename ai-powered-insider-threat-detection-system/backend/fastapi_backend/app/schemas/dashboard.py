"""
Dashboard Composite Schemas
"""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DashboardStats(BaseModel):
    """Dashboard statistics for stat cards"""
    total_users: int
    high_risk_count: int
    medium_risk_count: int
    red_team_count: int
    active_model_count: int
    total_alerts_24h: int

    model_config = ConfigDict(from_attributes=True)


class DashboardOverview(BaseModel):
    """Dashboard overview response"""
    stats: DashboardStats
    recent_alerts: List["AlertEvent"]
    active_model_run_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class UserRankedRow(BaseModel):
    """User row in the anomaly table"""
    user_id: UUID
    username: str
    full_name: Optional[str]
    department: Optional[str]
    composite_score: float
    risk_level: str  # low, medium, high, critical
    is_red_team: bool
    isolation_forest_score: Optional[float]
    oneclass_svm_score: Optional[float]
    autoencoder_score: Optional[float]
    out_of_session_access: Optional[int]
    calculation_date: date

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(BaseModel):
    """Full user detail with features and scores"""
    # User info
    user_id: UUID
    username: str
    full_name: Optional[str]
    department: Optional[str]
    is_active: bool
    created_at: datetime
    
    # Latest features
    behavioral_features: Optional[dict] = None
    graph_features: Optional[dict] = None
    
    # Latest anomaly scores
    anomaly_scores: Optional[dict] = None
    
    # XAI explanations
    xai_explanations: Optional[List[dict]] = None
    
    # Red team status
    is_red_team: bool = False
    red_team_flags: Optional[List[dict]] = None

    model_config = ConfigDict(from_attributes=True)


class ScatterPoint(BaseModel):
    """Point for scatter plot chart"""
    user_id: UUID
    username: str
    iso_score: float
    ae_score: float
    is_red_team: bool
    risk_level: str
    composite_score: float

    model_config = ConfigDict(from_attributes=True)


class AlertEvent(BaseModel):
    """Alert event for timeline panel"""
    event_id: UUID
    user_id: UUID
    username: str
    event_type: str  # anomaly_detected, high_risk, red_team_flagged
    score: float
    risk_level: str
    is_red_team: bool
    timestamp: datetime
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
