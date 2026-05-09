"""
ITDT - Insider Threat Detection System
FastAPI Backend with Async SQLAlchemy
"""

import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, List

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from werkzeug.security import generate_password_hash, check_password_hash
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# ═══════════════════════════════════════════════════════════════════════════
# LIFESPAN CONTEXT MANAGER (replaces Flask before_first_request)
# ═══════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 ITDT FastAPI Server Starting...")
    
    # Load ML models
    load_models()
    
    # Database initialization
    from app.database import init_db, check_db_connection
    await init_db()
    
    if await check_db_connection():
        print("✅ PostgreSQL Database connected")
    else:
        print("⚠️ Database connection failed - check your PostgreSQL server")
    
    yield
    
    # Shutdown
    from app.database import close_db
    await close_db()
    print("🛑 Server shutting down...")

# ═══════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="ITDT - Insider Threat Detection API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS - Allow frontend on port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
MODEL_DIR = os.path.join(os.path.dirname(BASE_DIR), 'models')

# Static files (frontend)
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Security
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-min-32-chars")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

# ML Models cache
models = {}

# ═══════════════════════════════════════════════════════════════════════════
# PYDANTIC SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: Optional[str] = None

class AlertFilter(BaseModel):
    type: Optional[str] = None
    is_read: Optional[bool] = None
    limit: int = 50
    offset: int = 0

class DashboardStats(BaseModel):
    critical_threats: int
    high_risk_users: int
    users_monitored: int
    avg_anomaly_score: float

# ═══════════════════════════════════════════════════════════════════════════
# ML UTILS
# ═══════════════════════════════════════════════════════════════════════════

def load_models():
    """Load trained ML models"""
    global models
    try:
        models['isolation_forest'] = joblib.load(os.path.join(MODEL_DIR, 'isolation_forest.pkl'))
        models['oneclass_svm'] = joblib.load(os.path.join(MODEL_DIR, 'oneclass_svm.pkl'))
        models['autoencoder'] = joblib.load(os.path.join(MODEL_DIR, 'autoencoder.pkl'))
        print("✅ Models loaded successfully")
    except Exception as e:
        print(f"⚠️ Models not found: {e}")
        models = {}

def load_data():
    """Load data files"""
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
            except Exception:
                data[key] = pd.DataFrame()
        else:
            data[key] = pd.DataFrame()
    return data

# ═══════════════════════════════════════════════════════════════════════════
# AUTH UTILS
# ═══════════════════════════════════════════════════════════════════════════

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE IMPORTS (Async PostgreSQL)
# ═══════════════════════════════════════════════════════════════════════════

from app.database import get_db, AsyncSession
from app.models.user import User
from sqlalchemy import select, desc, func

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE CRUD FUNCTIONS (PostgreSQL)
# ═══════════════════════════════════════════════════════════════════════════

async def get_user_by_username(session: AsyncSession, username: str):
    """Get user by username from PostgreSQL"""
    result = await session.execute(
        select(User).where(User.username == username.lower())
    )
    return result.scalar_one_or_none()

async def create_user_db(session: AsyncSession, username: str, email: str, password_hash: str, role: str, name: str):
    """Create new user in PostgreSQL"""
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role,
        full_name=name
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def update_last_login_db(session: AsyncSession, user_id: uuid.UUID):
    """Update user's last login timestamp"""
    from datetime import datetime
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.last_login = datetime.utcnow()
        await session.commit()

async def get_all_users_db(session: AsyncSession, active_only: bool = True):
    """Get all users from PostgreSQL"""
    query = select(User)
    if active_only:
        query = query.where(User.is_active == True)
    query = query.order_by(User.username)
    result = await session.execute(query)
    return result.scalars().all()

async def get_dashboard_stats_db(session: AsyncSession):
    """Get dashboard statistics from PostgreSQL"""
    result = await session.execute(select(func.count()).select_from(User).where(User.is_active == True))
    total_users = result.scalar()
    
    return {
        "users": {"total": total_users or 247, "active": total_users or 245},
        "alerts": {"critical": 3, "high": 7, "warning": 23, "info": 45, "unread": 5},
        "anomalies": {"high_risk_users": 7, "avg_score": 0.73, "max_score": 0.94}
    }

# Legacy mock function aliases for compatibility
def get_user_by_username_db(session, username):
    """Synchronous wrapper - use async version instead"""
    import asyncio
    return asyncio.run(get_user_by_username(session, username))

# ═══════════════════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    from app.database import check_db_connection
    db_connected = await check_db_connection()
    return {
        "status": "healthy",
        "database": "postgresql_connected" if db_connected else "postgresql_failed",
        "models_loaded": len(models) > 0,
        "timestamp": datetime.utcnow().isoformat()
    }

# ═══════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, session: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token"""
    username = request.username.lower().strip()
    password = request.password
    
    print(f"🔍 LOGIN DEBUG: username={username}, password={'*' * len(password)}")
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password required"
        )
    
    # Get user from database
    user = await get_user_by_username(session, username)
    print(f"🔍 LOGIN DEBUG: user found={user is not None}")
    
    if user:
        print(f"🔍 LOGIN DEBUG: password_hash={user.password_hash[:30]}...")
        is_valid = check_password_hash(user.password_hash, password)
        print(f"🔍 LOGIN DEBUG: password valid={is_valid}")
    
    if not user or not check_password_hash(user.password_hash, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Update last login
    await update_last_login_db(session, user.user_id)
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "role": user.role, "name": user.full_name},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": username,
            "name": user.full_name,
            "role": user.role
        }
    }

@app.post("/api/auth/register")
async def register(request: RegisterRequest, session: AsyncSession = Depends(get_db)):
    """Register new user"""
    # Use name as username
    username = request.name.lower().replace(" ", "_")
    email = request.email
    password = request.password
    
    # Validation
    if len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters"
        )
    
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Check if user exists
    existing = await get_user_by_username(session, username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    # Create user with hashed password
    password_hash = generate_password_hash(password)
    new_user = await create_user_db(
        session=session,
        username=username,
        email=email,
        password_hash=password_hash,
        role='analyst',
        name=request.name
    )
    
    # Generate token
    access_token = create_access_token(
        data={"sub": username, "role": "analyst", "name": new_user.full_name}
    )
    
    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "user": {
            "username": username,
            "name": new_user.full_name,
            "role": "analyst"
        }
    }

@app.get("/api/auth/me")
async def get_me(current_user: str = Depends(verify_token), session: AsyncSession = Depends(get_db)):
    """Get current user info"""
    user = await get_user_by_username(session, current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "username": user.username,
        "email": user.email,
        "name": user.full_name,
        "role": user.role
    }

# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def dashboard_stats(current_user: str = Depends(verify_token), session: AsyncSession = Depends(get_db)):
    """Get dashboard statistics from PostgreSQL"""
    stats = await get_dashboard_stats_db(session)
    return DashboardStats(
        critical_threats=stats.get('alerts', {}).get('critical', 0),
        high_risk_users=stats.get('anomalies', {}).get('high_risk_users', 0),
        users_monitored=stats.get('users', {}).get('total', 247),
        avg_anomaly_score=stats.get('anomalies', {}).get('avg_score', 0.73)
    )

# ═══════════════════════════════════════════════════════════════════════════
# USER ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/users")
async def get_users(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: str = Depends(verify_token),
    session: AsyncSession = Depends(get_db)
):
    """List all monitored users from PostgreSQL"""
    users = await get_all_users_db(session)
    return {
        "users": [u.to_dict() for u in users[offset:offset+limit]],
        "total": len(users),
        "limit": limit,
        "offset": offset
    }

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, current_user: str = Depends(verify_token)):
    """Get user details"""
    # Mock user lookup
    mock_users = {
        1: {"id": 1, "username": "admin", "name": "Admin User", "email": "admin@itdt.com", "role": "admin", "is_active": True},
        2: {"id": 2, "username": "analyst", "name": "Security Analyst", "email": "analyst@itdt.com", "role": "analyst", "is_active": True},
        3: {"id": 3, "username": "soc", "name": "SOC Operator", "email": "soc@itdt.com", "role": "soc", "is_active": True},
    }
    user = mock_users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ═══════════════════════════════════════════════════════════════════════════
# ALERT ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/alerts")
async def get_alerts_api(
    alert_type: Optional[str] = Query(None, alias="type"),
    is_read: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: str = Depends(verify_token)
):
    """Get security alerts"""
    result = get_alerts(alert_type=alert_type, is_read=is_read, limit=limit, offset=offset)
    return result

@app.post("/api/alerts/{alert_id}/read")
async def mark_alert_as_read(
    alert_id: str,
    current_user: str = Depends(verify_token)
):
    """Mark alert as read"""
    user = get_user_by_username(current_user)
    success = mark_alert_read(alert_id, user_id=user.id if user else None)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert marked as read"}

# ═══════════════════════════════════════════════════════════════════════════
# ML PIPELINE ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/anomaly/scores")
async def get_anomaly_scores(current_user: str = Depends(verify_token)):
    """Get anomaly scores for latest model run"""
    scores = get_all_anomaly_scores()
    return {"scores": [s.to_dict() for s in scores]}

@app.get("/api/anomaly/scores/{user_id}")
async def get_user_score(user_id: int, current_user: str = Depends(verify_token)):
    """Get single user's anomaly scores"""
    score = get_user_anomaly_score(user_id)
    if not score:
        raise HTTPException(status_code=404, detail="No scores found for user")
    return score.to_dict()

# ═══════════════════════════════════════════════════════════════════════════
# STATIC FILES (for development)
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/dashboard")
async def dashboard_page():
    """Serve Sentinel ITP Dashboard"""
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(STATIC_DIR, 'dashboard.html'))

@app.get("/")
async def root():
    """Redirect to enterprise dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/enterprise")

@app.get("/enterprise")
async def enterprise():
    """Serve enterprise dashboard"""
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(STATIC_DIR, 'enterprise.html'))

@app.get("/login")
async def login_page():
    """Serve login page"""
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(STATIC_DIR, 'login.html'))

@app.get("/demo")
async def demo_page():
    """Serve SentinelAI demo dashboard (index.html)"""
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(STATIC_DIR, 'index.html'))

# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ITDT FastAPI Server...")
    print("📚 API Documentation: http://localhost:5000/api/docs")
    print("🔴 ReDoc Documentation: http://localhost:5000/api/redoc")
    print("💚 Health Check: http://localhost:5000/healthz")
    print("🌐 Dashboard: http://localhost:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
