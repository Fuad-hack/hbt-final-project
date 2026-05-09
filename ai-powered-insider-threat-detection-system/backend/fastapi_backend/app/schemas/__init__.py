"""
Pydantic v2 Schemas for request/response validation
"""

from app.schemas.user import UserCreate, UserResponse, UserList
from app.schemas.logs import LoginSessionResponse, FileAccessResponse, USBUsageResponse, EmailResponse
from app.schemas.features import (
    BehavioralFeatureResponse,
    GraphFeatureResponse,
    NLPEmailFeatureResponse,
    MergedFeatureResponse
)
from app.schemas.ml import (
    ModelRunCreate,
    ModelRunResponse,
    AnomalyScoreResponse,
    AnomalyScoreList
)
from app.schemas.xai import XAIExplanationResponse
from app.schemas.dashboard import (
    DashboardOverview,
    UserRankedRow,
    UserDetailResponse,
    ScatterPoint,
    AlertEvent,
    DashboardStats
)

__all__ = [
    # User
    "UserCreate",
    "UserResponse",
    "UserList",
    # Logs
    "LoginSessionResponse",
    "FileAccessResponse",
    "USBUsageResponse",
    "EmailResponse",
    # Features
    "BehavioralFeatureResponse",
    "GraphFeatureResponse",
    "NLPEmailFeatureResponse",
    "MergedFeatureResponse",
    # ML
    "ModelRunCreate",
    "ModelRunResponse",
    "AnomalyScoreResponse",
    "AnomalyScoreList",
    # XAI
    "XAIExplanationResponse",
    # Dashboard
    "DashboardOverview",
    "UserRankedRow",
    "UserDetailResponse",
    "ScatterPoint",
    "AlertEvent",
    "DashboardStats",
]
