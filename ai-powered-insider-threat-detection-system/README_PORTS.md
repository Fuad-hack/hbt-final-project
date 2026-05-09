# ITDT - Port Configuration (3000 + 5000)

## 🎯 Server Konfiqurasiyası

| Server | Port | URL | Təsvir |
|--------|------|-----|--------|
| **Frontend** | 3000 | http://localhost:3000 | HTML/CSS/JS faylları |
| **Backend** | 5000 | http://localhost:5000 | FastAPI + PostgreSQL |

## 🚀 Başlatma

### Terminal 1: Backend (Port 5000)
```bash
cd backend
python run.py
```

### Terminal 2: Frontend (Port 3000)
```bash
cd frontend
python -m http.server 3000
```

**Vəya PowerShell:**
```powershell
.\start-frontend.ps1
```

## 🔗 URL-lər

| Səhifə | URL |
|--------|-----|
| Login | http://localhost:3000/login.html |
| Dashboard | http://localhost:3000/dashboard.html |
| Enterprise | http://localhost:3000/enterprise.html |
| API Docs | http://localhost:5000/api/docs |

## ⚙️ CORS Konfiqurasiya

Backend bu origin-lərə icazə verir:
- http://localhost:3000
- http://localhost:5000
- http://127.0.0.1:3000
- http://127.0.0.1:5000

## 🔧 Frontend JS Faylları

Hər üç JS faylı backend-ə port 5000 üzərindən qoşulur:

```javascript
// login.js, enterprise.js, dashboard-api.js
const API_BASE_URL = 'http://localhost:5000';
```

## 🧪 Test

```bash
# Backend health check
curl http://localhost:5000/healthz

# Login test
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 📝 Qeydlər

- Frontend port 3000-də **statik fayl server** kimi işləyir
- Backend port 5000-də **FastAPI** ilə işləyir
- CORS icazələri ilə bir-birinə qoşula bilirlər
- Login token-ları browser localStorage-da saxlanılır

---

**Hazırsınız!** 🚀
