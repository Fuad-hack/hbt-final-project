# PostgreSQL Setup Guide for ITDT FastAPI Backend

## 1. Install PostgreSQL

### Windows
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer, set password for `postgres` user
3. Add to PATH: `C:\Program Files\PostgreSQL\15\bin`

### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql-15 postgresql-contrib
sudo systemctl start postgresql
```

## 2. Create Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Or on Windows (from cmd/psql)
psql -U postgres

# In psql shell:
CREATE DATABASE threatwatch;
CREATE USER itdt_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE threatwatch TO itdt_user;
\q
```

## 3. Run Schema SQL

```bash
# Apply the schema
psql -U postgres -d threatwatch -f backend/database/schema.sql
```

Or manually:
```bash
psql -U postgres -d threatwatch
\i backend/database/schema.sql
```

## 4. Configure Environment

Create `backend/.env` file:

```env
# Database
DATABASE_URL=postgresql+asyncpg://itdt_user:your_password@localhost:5432/threatwatch
DATABASE_SCHEMA=threat_detection

# Security
SECRET_KEY=your-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Anomaly Thresholds
COMPOSITE_HIGH_THRESHOLD=0.55
COMPOSITE_MEDIUM_THRESHOLD=0.38

# Redis (for future Celery)
REDIS_URL=redis://localhost:6379/0
```

## 5. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 6. Run the Server

```bash
python run.py
```

## 7. Verify Connection

Check health endpoint:
```bash
curl http://localhost:8000/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "database": "postgresql_connected",
  "models_loaded": true,
  "timestamp": "2024-01-18T12:00:00"
}
```

## Troubleshooting

### "Connection refused" error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                # macOS
```

### "Database does not exist"
```bash
# Create database manually
psql -U postgres -c "CREATE DATABASE threatwatch;"
```

### "Schema does not exist"
```bash
# Create schema manually
psql -U postgres -d threatwatch -c "CREATE SCHEMA threat_detection;"
```

### Permission denied
```bash
# Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE threatwatch TO itdt_user;"
```

## Default Users (After Migration)

The system will auto-create these users:
- `admin` / `admin123` (Admin role)
- `analyst` / `analyst123` (Analyst role)
- `soc` / `soc123` (SOC role)

## Database Schema Overview

```
threatwatch database
├── threat_detection schema
│   ├── users (UUID PK)
│   ├── login_sessions (FK → users)
│   ├── file_access_logs (FK → users)
│   ├── usb_usage_logs (FK → users)
│   ├── email_logs (FK → users)
│   ├── behavioral_features (FK → users)
│   ├── graph_features (FK → users)
│   ├── merged_features (FK → users)
│   ├── model_runs
│   ├── anomaly_scores (FK → users, model_runs)
│   ├── xai_explanations (FK → users, anomaly_scores)
│   └── red_team_flags (FK → users)
```

## Useful Commands

```bash
# Connect to database
psql -U postgres -d threatwatch

# List tables
\dt threat_detection.*

# Count users
SELECT COUNT(*) FROM threat_detection.users;

# Check recent logins
SELECT * FROM threat_detection.login_sessions ORDER BY login_time DESC LIMIT 5;
```
