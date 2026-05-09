"""
ITDT Database Models
SQLAlchemy ORM models for Insider Threat Detection System
"""

from datetime import datetime

# Import db with fallback for FastAPI mode
try:
    from . import db
    if db is None:
        raise ImportError("Database not initialized")
except ImportError:
    # Create a dummy db for type checking
    class DummyDB:
        Model = object
        Column = lambda *args, **kwargs: None
        Integer = String = DateTime = Boolean = ForeignKey = JSON = lambda: None
        relationship = backref = lazy = foreign_keys = lambda *args, **kwargs: None
    db = DummyDB()


class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='analyst')  # admin, analyst, soc
    name = db.Column(db.String(100))
    department = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    alerts = db.relationship('Alert', backref='assigned_user', lazy='dynamic', 
                             foreign_keys='Alert.user_id')
    activities = db.relationship('UserActivity', backref='user', lazy='dynamic')
    anomaly_scores = db.relationship('AnomalyScore', backref='user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'department': self.department,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Alert(db.Model):
    """Security alerts and notifications"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.String(20), unique=True, index=True)  # Format: ALT-001
    type = db.Column(db.String(20), default='info')  # critical, warning, info
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    anomaly_score = db.Column(db.Float)
    source_ip = db.Column(db.String(45))
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'user_id': self.user_id,
            'user_name': self.assigned_user.name if self.assigned_user else None,
            'anomaly_score': self.anomaly_score,
            'is_read': self.is_read,
            'is_resolved': self.is_resolved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'time_ago': self.get_time_ago()
        }
    
    def get_time_ago(self):
        """Convert timestamp to human readable time ago"""
        if not self.created_at:
            return 'Unknown'
        
        diff = datetime.utcnow() - self.created_at
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return 'Just now'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours} hour{"s" if hours > 1 else ""} ago'
        else:
            days = int(seconds / 86400)
            return f'{days} day{"s" if days > 1 else ""} ago'
    
    def __repr__(self):
        return f'<Alert {self.alert_id}>'


class UserActivity(db.Model):
    """User activity logs for behavior analysis"""
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    activity_type = db.Column(db.String(50), nullable=False, index=True)  # login, file_access, email, usb
    description = db.Column(db.Text)
    source_ip = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    # Activity details
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    email_recipient = db.Column(db.String(100))
    usb_device_id = db.Column(db.String(100))
    
    risk_level = db.Column(db.String(20), default='low')  # low, medium, high, critical
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'activity_type': self.activity_type,
            'description': self.description,
            'source_ip': self.source_ip,
            'file_name': self.file_name,
            'risk_level': self.risk_level,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<UserActivity {self.user_id}:{self.activity_type}>'


class AnomalyScore(db.Model):
    """ML model anomaly scores for users"""
    __tablename__ = 'anomaly_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Individual model scores
    isolation_forest = db.Column(db.Float)
    oneclass_svm = db.Column(db.Float)
    autoencoder = db.Column(db.Float)
    
    # Combined score
    combined_score = db.Column(db.Float, index=True)
    is_anomaly = db.Column(db.Boolean, default=False)
    
    # Feature importance (JSON for flexibility)
    top_features = db.Column(db.JSON)
    
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'isolation_forest': round(self.isolation_forest, 4) if self.isolation_forest else None,
            'oneclass_svm': round(self.oneclass_svm, 4) if self.oneclass_svm else None,
            'autoencoder': round(self.autoencoder, 4) if self.autoencoder else None,
            'combined': round(self.combined_score, 4) if self.combined_score else None,
            'is_anomaly': self.is_anomaly,
            'top_features': self.top_features,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }
    
    def __repr__(self):
        return f'<AnomalyScore {self.user_id}:{self.combined_score}>'


class AuditLog(db.Model):
    """Audit trail for compliance and security"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    action = db.Column(db.String(100), nullable=False)  # login, logout, view_user, export_data
    resource = db.Column(db.String(100))  # users, alerts, reports
    resource_id = db.Column(db.String(50))
    details = db.Column(db.JSON)  # Flexible JSON for action-specific data
    
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'System',
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'success': self.success,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action}:{self.resource}>'


class RedTeamLog(db.Model):
    """Red team exercise logs"""
    __tablename__ = 'red_team_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.String(20), unique=True, index=True)  # RTE-001
    
    # Attacker info
    simulated_user = db.Column(db.String(50))  # Red team member
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Attack details
    attack_type = db.Column(db.String(50))  # phishing, usb_drop, credential_theft
    description = db.Column(db.Text)
    techniques = db.Column(db.JSON)  # MITRE ATT&CK techniques
    
    # Results
    success = db.Column(db.Boolean)
    detection_time = db.Column(db.Integer)  # Minutes to detection
    was_detected = db.Column(db.Boolean, default=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'exercise_id': self.exercise_id,
            'simulated_user': self.simulated_user,
            'target_user': self.target_user.name if self.target_user else None,
            'attack_type': self.attack_type,
            'description': self.description,
            'techniques': self.techniques,
            'success': self.success,
            'was_detected': self.was_detected,
            'detection_time': self.detection_time,
            'started_at': self.started_at.isoformat() if self.started_at else None
        }
    
    def __repr__(self):
        return f'<RedTeamLog {self.exercise_id}>'


class GraphNode(db.Model):
    """Graph nodes for relationship analysis"""
    __tablename__ = 'graph_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(20), unique=True, index=True)  # USR-001
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    node_type = db.Column(db.String(20), default='user')  # user, file, device
    label = db.Column(db.String(100))
    risk_score = db.Column(db.Float, default=0.0)
    
    # Graph visualization data
    x_pos = db.Column(db.Float)
    y_pos = db.Column(db.Float)
    size = db.Column(db.Float, default=10.0)
    color = db.Column(db.String(7), default='#185FA5')  # Hex color
    
    is_flagged = db.Column(db.Boolean, default=False)
    
    # Relationships
    edges_source = db.relationship('GraphEdge', backref='source_node', lazy='dynamic',
                                  foreign_keys='GraphEdge.source_id')
    edges_target = db.relationship('GraphEdge', backref='target_node', lazy='dynamic',
                                  foreign_keys='GraphEdge.target_id')
    
    def to_dict(self):
        return {
            'id': self.node_id,
            'type': self.node_type,
            'label': self.label,
            'risk_score': self.risk_score,
            'x': self.x_pos,
            'y': self.y_pos,
            'size': self.size,
            'color': self.color,
            'is_flagged': self.is_flagged
        }
    
    def __repr__(self):
        return f'<GraphNode {self.node_id}>'


class GraphEdge(db.Model):
    """Graph edges for relationship connections"""
    __tablename__ = 'graph_edges'
    
    id = db.Column(db.Integer, primary_key=True)
    
    source_id = db.Column(db.String(20), db.ForeignKey('graph_nodes.node_id'), nullable=False)
    target_id = db.Column(db.String(20), db.ForeignKey('graph_nodes.node_id'), nullable=False)
    
    edge_type = db.Column(db.String(50))  # shared_file, email, usb_access
    weight = db.Column(db.Float, default=1.0)
    
    is_flagged = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'source': self.source_id,
            'target': self.target_id,
            'type': self.edge_type,
            'weight': self.weight,
            'is_flagged': self.is_flagged
        }
    
    def __repr__(self):
        return f'<GraphEdge {self.source_id}->{self.target_id}>'
