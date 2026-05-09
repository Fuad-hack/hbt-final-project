"""
ITDT Database Module
SQLAlchemy models and database configuration
"""

from datetime import datetime
import os

# Try Flask imports (for backward compatibility)
try:
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate
    db = SQLAlchemy()
    migrate = Migrate()
    FLASK_MODE = True
except ImportError:
    # FastAPI mode - no Flask dependencies
    db = None
    migrate = None
    FLASK_MODE = False

def init_db(app):
    """Initialize database with Flask app"""
    if not FLASK_MODE:
        # FastAPI mode - skip Flask initialization
        return
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'sqlite:///itdt.db'  # Default: SQLite for development
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables and default data
    with app.app_context():
        db.create_all()
        create_default_users()

def create_default_users():
    """Create default users if they don't exist"""
    if not FLASK_MODE:
        return
    
    try:
        from werkzeug.security import generate_password_hash
    except ImportError:
        return
    
    # Check if admin exists
    from .models import User
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@itdt.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            name='System Administrator'
        )
        db.session.add(admin)
    
    # Check if analyst exists
    if not User.query.filter_by(username='analyst').first():
        analyst = User(
            username='analyst',
            email='analyst@itdt.com',
            password_hash=generate_password_hash('analyst123'),
            role='analyst',
            name='Security Analyst'
        )
        db.session.add(analyst)
    
    # Check if soc exists
    if not User.query.filter_by(username='soc').first():
        soc = User(
            username='soc',
            email='soc@itdt.com',
            password_hash=generate_password_hash('soc123'),
            role='soc',
            name='SOC Operator'
        )
        db.session.add(soc)
    
    db.session.commit()

# Import models for easy access
from .models import User, Alert, UserActivity, AnomalyScore, AuditLog, RedTeamLog

__all__ = [
    'db', 
    'migrate', 
    'init_db',
    'FLASK_MODE',
    'User', 
    'Alert', 
    'UserActivity', 
    'AnomalyScore', 
    'AuditLog',
    'RedTeamLog'
]
