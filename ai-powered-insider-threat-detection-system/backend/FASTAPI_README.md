# ITDT FastAPI Backend

## Migration from Flask to FastAPI

### What's New

✅ **FastAPI** - Modern, fast (high-performance) web framework  
✅ **Auto-generated API Docs** - Swagger UI at `/api/docs`  
✅ **Pydantic Validation** - Automatic request/response validation  
✅ **Type Hints** - Full Python type annotation support  
✅ **Async Support** - Native async/await support  

### API Endpoints (Same as Flask)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with JWT token |
| POST | `/api/auth/register` | Register new user |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/users` | List all users |
| GET | `/api/users/{id}` | Get user details |
| GET | `/api/alerts` | Get security alerts |
| POST | `/api/alerts/{id}/read` | Mark alert as read |
| GET | `/api/anomaly/scores` | Get all anomaly scores |
| GET | `/api/anomaly/scores/{user_id}` | Get user score |
| GET | `/healthz` | Health check |

### Running the Server

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python run.py

# Or directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/healthz

### Testing

```bash
# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test dashboard stats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/dashboard/stats
```

### Frontend Compatibility

The frontend JavaScript already works with these endpoints:
- `login.js` → `/api/auth/login`
- `enterprise.js` → `/api/dashboard/stats`, `/api/alerts`

No frontend changes needed!

### Database

Uses the same database:
- SQLite: `backend/itdt.db`
- PostgreSQL: `threat_detection` schema

Models: `User`, `Alert`, `UserActivity`, `AnomalyScore`, etc.

### Environment Variables

Create `.env` file:
```
JWT_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///itdt.db
```

### Differences from Flask

| Feature | Flask | FastAPI |
|---------|-------|---------|
| Request validation | Manual | Automatic (Pydantic) |
| API docs | None | Auto-generated |
| Error handling | Manual | Automatic |
| Type hints | Optional | Required |
| Async | Limited | Native |

### Troubleshooting

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Database not found:**
```bash
# Database will be auto-created on first run
python -c "from database import init_db; init_db(app)"
```

### Migration Checklist

- [x] Auth endpoints migrated
- [x] Dashboard endpoints migrated
- [x] User endpoints migrated
- [x] Alert endpoints migrated
- [x] Anomaly endpoints migrated
- [x] Database compatibility maintained
- [x] Frontend compatibility verified
- [ ] WebSocket support (next phase)
- [ ] Celery tasks (next phase)
