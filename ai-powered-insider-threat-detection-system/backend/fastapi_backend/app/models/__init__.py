"""
ITDT ORM Models Package
SQLAlchemy 2.0 Declarative Models
"""

from app.models.user import User
from app.models.logs import LoginSession, FileAccessLog, USBUsageLog, EmailLog
from app.models.features import BehavioralFeature, GraphFeature, NLPEmailFeature, MergedFeature
from app.models.ml import ModelRun, AnomalyScore
from app.models.xai import XAIExplanation
from app.models.red_team import RedTeamFlag

__all__ = [
    # User
    "User",
    # Logs
    "LoginSession",
    "FileAccessLog", 
    "USBUsageLog",
    "EmailLog",
    # Features
    "BehavioralFeature",
    "GraphFeature",
    "NLPEmailFeature",
    "MergedFeature",
    # ML
    "ModelRun",
    "AnomalyScore",
    # XAI
    "XAIExplanation",
    # Red Team
    "RedTeamFlag",
]
