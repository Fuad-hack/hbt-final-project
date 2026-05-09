"""
Database Utility Functions
Helper functions for common database operations
"""

from . import db
from .models import User, Alert, UserActivity, AnomalyScore, AuditLog
from datetime import datetime, timedelta


# ═════════════════════════════════════════════════════════════════
# USER OPERATIONS
# ═════════════════════════════════════════════════════════════════

def get_user_by_username(username):
    """Get user by username (case insensitive)"""
    return User.query.filter(
        db.func.lower(User.username) == username.lower()
    ).first()


def get_user_by_email(email):
    """Get user by email"""
    return User.query.filter(
        db.func.lower(User.email) == email.lower()
    ).first()


def create_user(username, email, password_hash, role='analyst', name=None):
    """Create a new user"""
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role,
        name=name or username.title()
    )
    db.session.add(user)
    db.session.commit()
    return user


def update_last_login(user_id):
    """Update user's last login timestamp"""
    user = User.query.get(user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.session.commit()


def get_all_users(active_only=True):
    """Get all users with optional filtering"""
    query = User.query
    if active_only:
        query = query.filter_by(is_active=True)
    return query.order_by(User.username).all()


# ═════════════════════════════════════════════════════════════════
# ALERT OPERATIONS
# ═════════════════════════════════════════════════════════════════

def create_alert(alert_type, title, message, user_id=None, anomaly_score=None, source_ip=None):
    """Create a new security alert"""
    # Generate alert ID
    last_alert = Alert.query.order_by(Alert.id.desc()).first()
    next_id = (last_alert.id + 1) if last_alert else 1
    alert_id = f'ALT-{next_id:03d}'
    
    alert = Alert(
        alert_id=alert_id,
        type=alert_type,
        title=title,
        message=message,
        user_id=user_id,
        anomaly_score=anomaly_score,
        source_ip=source_ip
    )
    db.session.add(alert)
    db.session.commit()
    return alert


def get_alerts(alert_type=None, is_read=None, limit=50, offset=0):
    """Get alerts with filtering"""
    query = Alert.query
    
    if alert_type and alert_type != 'all':
        query = query.filter_by(type=alert_type)
    
    if is_read is not None:
        query = query.filter_by(is_read=is_read)
    
    total = query.count()
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).offset(offset).all()
    
    return {
        'alerts': [a.to_dict() for a in alerts],
        'total': total,
        'unread': Alert.query.filter_by(is_read=False).count()
    }


def mark_alert_read(alert_id, user_id=None):
    """Mark an alert as read"""
    alert = Alert.query.filter_by(alert_id=alert_id).first()
    if alert:
        alert.is_read = True
        db.session.commit()
        
        # Log the action
        log_audit_action(
            user_id=user_id,
            action='mark_alert_read',
            resource='alerts',
            resource_id=alert_id
        )
        return True
    return False


def get_alert_stats():
    """Get alert statistics for dashboard"""
    stats = {
        'total': Alert.query.count(),
        'unread': Alert.query.filter_by(is_read=False).count(),
        'critical': Alert.query.filter_by(type='critical').count(),
        'warning': Alert.query.filter_by(type='warning').count(),
        'info': Alert.query.filter_by(type='info').count()
    }
    return stats


# ═════════════════════════════════════════════════════════════════
# ACTIVITY OPERATIONS
# ═════════════════════════════════════════════════════════════════

def log_activity(user_id, activity_type, description, **kwargs):
    """Log a user activity"""
    activity = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        description=description,
        source_ip=kwargs.get('ip_address'),
        user_agent=kwargs.get('user_agent'),
        file_name=kwargs.get('file_name'),
        file_size=kwargs.get('file_size'),
        email_recipient=kwargs.get('email_recipient'),
        usb_device_id=kwargs.get('usb_device_id'),
        risk_level=kwargs.get('risk_level', 'low')
    )
    db.session.add(activity)
    db.session.commit()
    return activity


def get_user_activities(user_id, limit=100, hours=None):
    """Get user activities with optional time filter"""
    query = UserActivity.query.filter_by(user_id=user_id)
    
    if hours:
        since = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(UserActivity.timestamp >= since)
    
    return query.order_by(UserActivity.timestamp.desc()).limit(limit).all()


def get_recent_activities(limit=50):
    """Get recent activities across all users"""
    return UserActivity.query.order_by(
        UserActivity.timestamp.desc()
    ).limit(limit).all()


# ═════════════════════════════════════════════════════════════════
# ANOMALY SCORE OPERATIONS
# ═════════════════════════════════════════════════════════════════

def save_anomaly_score(user_id, iso_score, svm_score, ae_score, top_features=None):
    """Save ML model anomaly scores"""
    combined = (iso_score + svm_score + ae_score) / 3
    
    score = AnomalyScore(
        user_id=user_id,
        isolation_forest=iso_score,
        oneclass_svm=svm_score,
        autoencoder=ae_score,
        combined_score=combined,
        is_anomaly=combined > 0.7,
        top_features=top_features
    )
    db.session.add(score)
    db.session.commit()
    return score


def get_user_anomaly_score(user_id):
    """Get latest anomaly score for a user"""
    return AnomalyScore.query.filter_by(user_id=user_id).order_by(
        AnomalyScore.calculated_at.desc()
    ).first()


def get_all_anomaly_scores(anomaly_only=False):
    """Get all anomaly scores"""
    query = AnomalyScore.query
    
    if anomaly_only:
        query = query.filter_by(is_anomaly=True)
    
    # Get latest score per user
    latest_scores = db.session.query(
        AnomalyScore.user_id,
        db.func.max(AnomalyScore.calculated_at).label('latest')
    ).group_by(AnomalyScore.user_id).subquery()
    
    return query.join(
        latest_scores,
        db.and_(
            AnomalyScore.user_id == latest_scores.c.user_id,
            AnomalyScore.calculated_at == latest_scores.c.latest
        )
    ).all()


def get_risk_distribution():
    """Get risk level distribution for dashboard charts"""
    scores = get_all_anomaly_scores()
    
    critical = sum(1 for s in scores if s.combined_score >= 0.8)
    high = sum(1 for s in scores if 0.6 <= s.combined_score < 0.8)
    medium = sum(1 for s in scores if 0.35 <= s.combined_score < 0.6)
    low = sum(1 for s in scores if s.combined_score < 0.35)
    
    return {
        'labels': ['Critical', 'High', 'Medium', 'Low'],
        'data': [critical, high, medium, low],
        'colors': ['#DC2626', '#D97706', '#7C3AED', '#059669']
    }


# ═════════════════════════════════════════════════════════════════
# AUDIT LOG OPERATIONS
# ═════════════════════════════════════════════════════════════════

def log_audit_action(user_id, action, resource, resource_id=None, 
                     details=None, success=True, error_message=None,
                     ip_address=None, user_agent=None):
    """Log an audit action"""
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        success=success,
        error_message=error_message,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.session.add(log)
    db.session.commit()
    return log


def get_audit_logs(user_id=None, action=None, resource=None, limit=100):
    """Get audit logs with filtering"""
    query = AuditLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action:
        query = query.filter_by(action=action)
    if resource:
        query = query.filter_by(resource=resource)
    
    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()


def get_login_history(user_id=None, hours=24):
    """Get recent login history"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = AuditLog.query.filter(
        AuditLog.action.in_(['login', 'logout']),
        AuditLog.timestamp >= since
    )
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    return query.order_by(AuditLog.timestamp.desc()).all()


# ═════════════════════════════════════════════════════════════════
# DASHBOARD STATISTICS
# ═════════════════════════════════════════════════════════════════

def check_db_connection():
    """Check if database connection is working"""
    try:
        from . import db
        db.session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_dashboard_stats():
    """Get all statistics for dashboard"""
    from sqlalchemy import func
    
    # User stats
    total_users = User.query.filter_by(is_active=True).count()
    
    # Activity stats (last 24 hours)
    day_ago = datetime.utcnow() - timedelta(hours=24)
    activities_24h = UserActivity.query.filter(
        UserActivity.timestamp >= day_ago
    ).count()
    
    # Anomaly stats
    latest_scores = db.session.query(
        func.max(AnomalyScore.combined_score).label('max_score'),
        func.avg(AnomalyScore.combined_score).label('avg_score')
    ).filter(
        AnomalyScore.calculated_at >= day_ago
    ).first()
    
    # Alert stats
    alert_stats = get_alert_stats()
    
    return {
        'users': {
            'total': total_users,
            'active': total_users  # All active users
        },
        'activities': {
            'total_24h': activities_24h,
            'avg_per_hour': round(activities_24h / 24, 1)
        },
        'anomalies': {
            'max_score': round(latest_scores.max_score, 3) if latest_scores.max_score else 0,
            'avg_score': round(latest_scores.avg_score, 3) if latest_scores.avg_score else 0,
            'high_risk_users': AnomalyScore.query.filter(
                AnomalyScore.combined_score >= 0.7
            ).count()
        },
        'alerts': alert_stats
    }
