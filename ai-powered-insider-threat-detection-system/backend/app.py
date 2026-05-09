"""
ITDT - Insider Threat Detection System
Flask-based REST API with SQLAlchemy Database
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import pandas as pd
import numpy as np
import joblib
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

CORS(app)
jwt = JWTManager(app)

# Paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

# ═════════════════════════════════════════════════════════════════
# DATABASE SETUP
# ═════════════════════════════════════════════════════════════════
from database import init_db, db
from database.models import User, Alert, UserActivity, AnomalyScore, AuditLog, RedTeamLog
from database.utils import (
    get_user_by_username, create_user, update_last_login,
    create_alert, get_alerts, mark_alert_read, get_alert_stats,
    log_activity, get_user_activities, get_recent_activities,
    save_anomaly_score, get_user_anomaly_score, get_all_anomaly_scores,
    get_risk_distribution, log_audit_action, get_dashboard_stats
)

# Initialize database
init_db(app)

# ═════════════════════════════════════════════════════════════════
# ML MODELS
# ═════════════════════════════════════════════════════════════════
models = {}

def load_models():
    """Load trained ML models"""
    global models
    try:
        models['isolation_forest'] = joblib.load(os.path.join(MODEL_DIR, 'isolation_forest.pkl'))
        models['oneclass_svm'] = joblib.load(os.path.join(MODEL_DIR, 'oneclass_svm.pkl'))
        models['autoencoder'] = joblib.load(os.path.join(MODEL_DIR, 'autoencoder.pkl'))
        print("✓ Models loaded successfully")
    except Exception as e:
        print(f"⚠ Error loading models: {e}")
        models = {}

def load_data():
    """Load all data files"""
    data = {}
    files = {
        'anomaly_scores': 'anomaly_scores.csv',
        'merged_features': 'merged_features.csv',
        'logins': 'logins.csv',
        'file_access': 'file_access.csv',
        'usb_usage': 'usb_usage.csv',
        'emails': 'emails.csv',
        'graph_features': 'graph_features.csv',
        'red_team_users': 'red_team_users.csv'
    }
    for key, filename in files.items():
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            try:
                data[key] = pd.read_csv(filepath)
            except Exception as e:
                print(f"⚠ Error loading {filename}: {e}")
                data[key] = pd.DataFrame()
        else:
            data[key] = pd.DataFrame()
    return data

# ═════════════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ═════════════════════════════════════════════════════════════════

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.get_json()
    username = data.get('username', '').lower()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Get user from database
    user = get_user_by_username(username)
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Update last login
    update_last_login(user.id)
    
    # Log the login action
    log_audit_action(
        user_id=user.id,
        action='login',
        resource='auth',
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    access_token = create_access_token(
        identity=username,
        additional_claims={'role': user.role, 'name': user.name}
    )
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'username': username,
            'name': user.name,
            'role': user.role
        }
    })

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    current_user = get_jwt_identity()
    claims = get_jwt()
    return jsonify({
        'username': current_user,
        'name': claims.get('name'),
        'role': claims.get('role')
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    username = data.get('username', '').lower().strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    role = data.get('role', 'analyst')
    
    # Validation
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if user exists in database
    if get_user_by_username(username):
        return jsonify({'error': 'Username already exists'}), 409
    
    if get_user_by_email(email):
        return jsonify({'error': 'Email already registered'}), 409
    
    # Valid roles
    valid_roles = ['admin', 'analyst', 'soc']
    if role not in valid_roles:
        role = 'analyst'
    
    # Create user in database
    password_hash = generate_password_hash(password)
    new_user = create_user(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role,
        name=username.title()
    )
    
    # Log registration
    log_audit_action(
        user_id=new_user.id,
        action='register',
        resource='users',
        resource_id=str(new_user.id),
        ip_address=request.remote_addr
    )
    
    # Generate token
    access_token = create_access_token(
        identity=username,
        additional_claims={'role': role, 'name': new_user.name}
    )
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'user': new_user.to_dict()
    }), 201

# ═════════════════════════════════════════════════════════════════
# DASHBOARD & DATA ROUTES
# ═════════════════════════════════════════════════════════════════

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    """Get dashboard statistics from database"""
    stats = get_dashboard_stats()
    return jsonify(stats)
    max_iso = iso_scores.max() if len(iso_scores) > 0 else 1
    max_svm = svm_scores.max() if len(svm_scores) > 0 else 1
    max_ae = ae_scores.max() if len(ae_scores) > 0 else 1
    
    normalized_iso = iso_scores / max_iso if max_iso > 0 else iso_scores
    normalized_svm = svm_scores / max_svm if max_svm > 0 else svm_scores
    normalized_ae = ae_scores / max_ae if max_ae > 0 else ae_scores
    
    # Combined anomaly score (average of normalized scores)
    combined_scores = (normalized_iso + normalized_svm + normalized_ae) / 3
    
    critical_threshold = 0.8
    critical_threats = int((combined_scores > critical_threshold).sum())
    high_risk_threshold = 0.6
    high_risk_users = int((combined_scores > high_risk_threshold).sum())
    
    avg_score = round(float(combined_scores.mean()), 3) if len(combined_scores) > 0 else 0
    
    red_team_count = int(scores_df.get('is_red_team', pd.Series([0]*total_users)).sum())
    
    return jsonify({
        'critical_threats': critical_threats,
        'avg_anomaly_score': avg_score,
        'red_team_flags': red_team_count,
        'active_models': 3,
        'total_users': total_users,
        'high_risk_users': high_risk_users,
        'last_updated': pd.Timestamp.now().isoformat()
    })

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with anomaly scores"""
    data = load_data()
    scores_df = data.get('anomaly_scores', pd.DataFrame())
    features_df = data.get('merged_features', pd.DataFrame())
    
    if scores_df.empty:
        return jsonify({'users': [], 'count': 0})
    
    # Merge with features for department info
    if not features_df.empty and 'user' in features_df.columns:
        # Add department if available in features
        pass
    
    # Process scores
    users = []
    for idx, row in scores_df.iterrows():
        # Calculate combined score
        iso = row.get('isolation_forest', 0)
        svm = row.get('oneclass_svm', 0)
        ae = row.get('autoencoder', 0)
        
        # Normalize (simple approach)
        score = float((iso + svm + ae) / 3)
        
        # Determine risk level
        if score >= 0.8:
            risk = 'critical'
        elif score >= 0.6:
            risk = 'high'
        elif score >= 0.35:
            risk = 'medium'
        else:
            risk = 'low'
        
        users.append({
            'id': str(row.get('user', f'USR-{idx}')),
            'name': str(row.get('user', f'User {idx}')),
            'department': 'Unknown',  # Add from features if available
            'risk_level': risk,
            'anomaly_score': round(score, 3),
            'is_red_team': bool(row.get('is_red_team', False)),
            'model_scores': {
                'isolation_forest': round(float(iso), 3),
                'oneclass_svm': round(float(svm), 3),
                'autoencoder': round(float(ae), 3)
            },
            'last_activity': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
        })
    
    # Sort by anomaly score descending
    users.sort(key=lambda x: x['anomaly_score'], reverse=True)
    
    return jsonify({
        'users': users,
        'count': len(users)
    })

@app.route('/api/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user_detail(user_id):
    """Get detailed information for a specific user"""
    data = load_data()
    scores_df = data.get('anomaly_scores', pd.DataFrame())
    features_df = data.get('merged_features', pd.DataFrame())
    logins_df = data.get('logins', pd.DataFrame())
    file_access_df = data.get('file_access', pd.DataFrame())
    usb_df = data.get('usb_usage', pd.DataFrame())
    emails_df = data.get('emails', pd.DataFrame())
    
    # Find user
    user_row = scores_df[scores_df['user'] == user_id]
    if user_row.empty:
        return jsonify({'error': 'User not found'}), 404
    
    row = user_row.iloc[0]
    
    # Get features for user
    features = {}
    if not features_df.empty and 'user' in features_df.columns:
        user_features = features_df[features_df['user'] == user_id]
        if not user_features.empty:
            features = user_features.iloc[0].drop(['user', 'is_red_team'], errors='ignore').to_dict()
    
    # Get activity counts
    login_count = 0
    if not logins_df.empty and 'user_id' in logins_df.columns:
        login_count = len(logins_df[logins_df['user_id'] == user_id])
    
    file_count = 0
    if not file_access_df.empty and 'user_id' in file_access_df.columns:
        file_count = len(file_access_df[file_access_df['user_id'] == user_id])
    
    usb_count = 0
    if not usb_df.empty and 'user_id' in usb_df.columns:
        usb_count = len(usb_df[usb_df['user_id'] == user_id])
    
    email_count = 0
    if not emails_df.empty and 'user_id' in emails_df.columns:
        email_count = len(emails_df[emails_df['user_id'] == user_id])
    
    # Calculate combined score
    iso = row.get('isolation_forest', 0)
    svm = row.get('oneclass_svm', 0)
    ae = row.get('autoencoder', 0)
    combined_score = float((iso + svm + ae) / 3)
    
    return jsonify({
        'id': user_id,
        'name': user_id,
        'department': 'Unknown',
        'risk_level': 'critical' if combined_score >= 0.8 else 'high' if combined_score >= 0.6 else 'medium' if combined_score >= 0.35 else 'low',
        'anomaly_score': round(combined_score, 3),
        'is_red_team': bool(row.get('is_red_team', False)),
        'model_scores': {
            'isolation_forest': round(float(iso), 3),
            'oneclass_svm': round(float(svm), 3),
            'autoencoder': round(float(ae), 3)
        },
        'features': features,
        'activity_summary': {
            'logins': login_count,
            'file_access': file_count,
            'usb_usage': usb_count,
            'emails': email_count
        }
    })

# ═════════════════════════════════════════════════════════════════
# ALERTS ROUTES
# ═════════════════════════════════════════════════════════════════

# Mock alerts database
ALERTS = [
    {
        'id': 'ALT-001',
        'type': 'critical',
        'title': 'Critical Anomaly Detected',
        'message': 'User shows anomaly score 0.94 — potential data exfiltration pattern',
        'user_id': 'USR-4821',
        'timestamp': pd.Timestamp.now() - pd.Timedelta(minutes=2),
        'read': False
    },
    {
        'id': 'ALT-002',
        'type': 'warning',
        'title': 'High Risk Activity',
        'message': 'User accessed 247 files after hours — bulk download suspected',
        'user_id': 'USR-3156',
        'timestamp': pd.Timestamp.now() - pd.Timedelta(minutes=15),
        'read': False
    },
    {
        'id': 'ALT-003',
        'type': 'warning',
        'title': 'USB Device Connected',
        'message': 'External storage device detected on workstation',
        'user_id': 'USR-7823',
        'timestamp': pd.Timestamp.now() - pd.Timedelta(minutes=32),
        'read': True
    }
]

@app.route('/api/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get all alerts"""
    alert_type = request.args.get('type', 'all')
    
    filtered_alerts = ALERTS
    if alert_type != 'all':
        filtered_alerts = [a for a in ALERTS if a['type'] == alert_type]
    
    # Convert timestamps to strings
    result = []
    for alert in filtered_alerts:
        alert_copy = alert.copy()
        alert_copy['timestamp'] = alert['timestamp'].isoformat()
        alert_copy['time_ago'] = get_time_ago(alert['timestamp'])
        result.append(alert_copy)
    
    return jsonify({
        'alerts': result,
        'count': len(result),
        'unread': len([a for a in ALERTS if not a['read']])
    })

@app.route('/api/alerts/<alert_id>/read', methods=['POST'])
@jwt_required()
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    for alert in ALERTS:
        if alert['id'] == alert_id:
            alert['read'] = True
            return jsonify({'message': 'Alert marked as read'})
    return jsonify({'error': 'Alert not found'}), 404

def get_time_ago(timestamp):
    """Convert timestamp to human readable time ago"""
    now = pd.Timestamp.now()
    diff = now - timestamp
    
    if diff < pd.Timedelta(minutes=1):
        return 'Just now'
    elif diff < pd.Timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif diff < pd.Timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    else:
        days = int(diff.total_seconds() / 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'

# ═════════════════════════════════════════════════════════════════
# CHART DATA ROUTES
# ═════════════════════════════════════════════════════════════════

@app.route('/api/charts/trend', methods=['GET'])
@jwt_required()
def get_trend_data():
    """Get anomaly trend data for charts"""
    data = load_data()
    scores_df = data.get('anomaly_scores', pd.DataFrame())
    
    # Generate 14 days of trend data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=14, freq='D')
    
    if scores_df.empty:
        # Return mock data
        trend = {
            'labels': [d.strftime('%b %d') for d in dates],
            'datasets': [
                {'label': 'Isolation Forest', 'data': [0.3 + i*0.05 for i in range(14)]},
                {'label': 'One-Class SVM', 'data': [0.4 + i*0.03 for i in range(14)]},
                {'label': 'Autoencoder', 'data': [0.35 + i*0.04 for i in range(14)]}
            ]
        }
    else:
        # Calculate actual trend from data
        iso_scores = scores_df.get('isolation_forest', pd.Series([0.5]*len(scores_df)))
        svm_scores = scores_df.get('oneclass_svm', pd.Series([0.5]*len(scores_df)))
        ae_scores = scores_df.get('autoencoder', pd.Series([0.5]*len(scores_df)))
        
        trend = {
            'labels': [d.strftime('%b %d') for d in dates],
            'datasets': [
                {'label': 'Isolation Forest', 'data': [round(float(iso_scores.mean()), 3)] * 14},
                {'label': 'One-Class SVM', 'data': [round(float(svm_scores.mean()), 3)] * 14},
                {'label': 'Autoencoder', 'data': [round(float(ae_scores.mean()), 3)] * 14}
            ]
        }
    
    return jsonify(trend)

@app.route('/api/charts/risk-distribution', methods=['GET'])
@jwt_required()
def get_risk_distribution():
    """Get risk level distribution for donut chart"""
    data = load_data()
    scores_df = data.get('anomaly_scores', pd.DataFrame())
    
    if scores_df.empty:
        distribution = {
            'labels': ['Critical', 'High', 'Medium', 'Low'],
            'data': [3, 7, 45, 192]  # Mock data
        }
    else:
        # Calculate from actual scores
        total = len(scores_df)
        iso = scores_df.get('isolation_forest', pd.Series([0]*total))
        svm = scores_df.get('oneclass_svm', pd.Series([0]*total))
        ae = scores_df.get('autoencoder', pd.Series([0]*total))
        
        combined = (iso + svm + ae) / 3
        
        critical = int((combined >= 0.8).sum())
        high = int((combined >= 0.6).sum()) - critical
        medium = int((combined >= 0.35).sum()) - critical - high
        low = total - critical - high - medium
        
        distribution = {
            'labels': ['Critical', 'High', 'Medium', 'Low'],
            'data': [critical, high, medium, low]
        }
    
    return jsonify(distribution)

# ═════════════════════════════════════════════════════════════════
# RED TEAM ROUTES
# ═════════════════════════════════════════════════════════════════

@app.route('/api/red-team/logs', methods=['GET'])
@jwt_required()
def get_red_team_logs():
    """Get red team activity logs"""
    data = load_data()
    red_team_df = data.get('red_team_users', pd.DataFrame())
    
    logs = []
    if not red_team_df.empty:
        for idx, row in red_team_df.iterrows():
            logs.append({
                'id': f'RTL-{idx:03d}',
                'user_id': str(row.get('user', f'RT-{idx}')),
                'activity': row.get('activity', 'Unknown activity'),
                'timestamp': row.get('timestamp', pd.Timestamp.now().isoformat()),
                'severity': row.get('severity', 'medium')
            })
    else:
        # Mock data
        logs = [
            {'id': 'RTL-001', 'user_id': 'RT-001', 'activity': 'Simulated phishing', 'timestamp': pd.Timestamp.now().isoformat(), 'severity': 'high'},
            {'id': 'RTL-002', 'user_id': 'RT-002', 'activity': 'USB drop test', 'timestamp': pd.Timestamp.now().isoformat(), 'severity': 'medium'}
        ]
    
    return jsonify({'logs': logs, 'count': len(logs)})

# ═════════════════════════════════════════════════════════════════
# GRAPH ANALYSIS ROUTES
# ═════════════════════════════════════════════════════════════════

@app.route('/api/graph/nodes', methods=['GET'])
@jwt_required()
def get_graph_nodes():
    """Get graph nodes (users) with risk levels"""
    data = load_data()
    scores_df = data.get('anomaly_scores', pd.DataFrame())
    graph_df = data.get('graph_features', pd.DataFrame())
    
    nodes = []
    for idx, row in scores_df.iterrows():
        user_id = str(row.get('user', f'USR-{idx}'))
        iso = row.get('isolation_forest', 0)
        svm = row.get('oneclass_svm', 0)
        ae = row.get('autoencoder', 0)
        score = float((iso + svm + ae) / 3)
        
        nodes.append({
            'id': user_id,
            'label': user_id,
            'risk_level': 'critical' if score >= 0.8 else 'high' if score >= 0.6 else 'medium' if score >= 0.35 else 'low',
            'score': round(score, 3),
            'is_red_team': bool(row.get('is_red_team', False))
        })
    
    return jsonify({'nodes': nodes})

@app.route('/api/graph/edges', methods=['GET'])
@jwt_required()
def get_graph_edges():
    """Get graph edges (relationships between users)"""
    data = load_data()
    file_access_df = data.get('file_access', pd.DataFrame())
    
    edges = []
    
    # Create edges based on shared file access
    if not file_access_df.empty and 'user_id' in file_access_df.columns and 'file_id' in file_access_df.columns:
        # Group by file to find users who accessed the same files
        file_groups = file_access_df.groupby('file_id')['user_id'].apply(list).to_dict()
        
        edge_id = 0
        for file_id, users in file_groups.items():
            if len(users) > 1:
                for i in range(len(users)):
                    for j in range(i + 1, len(users)):
                        edges.append({
                            'id': f'edge-{edge_id}',
                            'source': str(users[i]),
                            'target': str(users[j]),
                            'label': f'Shared: {file_id}',
                            'type': 'shared_resource'
                        })
                        edge_id += 1
                        
                        # Limit edges for performance
                        if edge_id >= 100:
                            break
                    if edge_id >= 100:
                        break
                if edge_id >= 100:
                    break
    
    return jsonify({'edges': edges})

# ═════════════════════════════════════════════════════════════════
# ML PREDICTION ROUTES
# ═════════════════════════════════════════════════════════════════

@app.route('/api/predict', methods=['POST'])
@jwt_required()
def predict():
    """Run ML prediction on new data"""
    if not models:
        return jsonify({'error': 'Models not loaded'}), 503
    
    data = request.get_json()
    features = data.get('features', [])
    
    if not features:
        return jsonify({'error': 'No features provided'}), 400
    
    try:
        X = np.array(features).reshape(1, -1)
        
        # Get predictions from each model
        iso_score = -models['isolation_forest'].score_samples(X)[0]
        svm_score = -models['oneclass_svm'].decision_function(X)[0]
        ae_pred = models['autoencoder'].predict(X)
        ae_score = np.mean((X - ae_pred) ** 2)
        
        combined_score = float((iso_score + svm_score + ae_score) / 3)
        
        return jsonify({
            'prediction': {
                'isolation_forest': round(float(iso_score), 4),
                'oneclass_svm': round(float(svm_score), 4),
                'autoencoder': round(float(ae_score), 4),
                'combined': round(combined_score, 4)
            },
            'is_anomaly': combined_score > 0.7,
            'confidence': round(min(combined_score * 100, 99), 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═════════════════════════════════════════════════════════════════
# SERVE FRONTEND
# ═════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve the login page"""
    return app.send_static_file('login.html')

@app.route('/dashboard')
@jwt_required()
def dashboard():
    """Serve the dashboard"""
    return app.send_static_file('dashboard.html')

@app.route('/enterprise')
@jwt_required()
def enterprise():
    """Serve the enterprise dashboard"""
    return app.send_static_file('enterprise.html')

# ═════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    load_models()
    print(" Starting ITDT API Server...")
    print(" API Documentation:")
    print("   POST /api/auth/login     - Authenticate")
    print("   POST /api/auth/register  - Register new user")
    print("   GET  /api/auth/me        - Current user info")
    print("   GET  /api/dashboard/stats - Dashboard statistics")
    print("   GET  /api/users          - List all users")
    print("   GET  /api/users/<id>     - User details")
    print("   GET  /api/alerts         - Security alerts")
    print("   GET  /api/charts/trend   - Anomaly trend data")
    print("   GET  /api/graph/nodes    - Graph nodes")
    print("   GET  /api/graph/edges    - Graph edges")
    print("\n📍 Web Interface: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
