# Sentinel ITP - Enterprise Insider Threat Protection

AI-Powered Insider Threat Detection and Investigation Platform with professional enterprise-grade dashboard.

## Project Structure

```
ai-powered-insider-threat-detection-system/
├── backend/                    # Flask REST API
│   ├── app.py                 # Main API server
│   ├── requirements.txt       # Backend dependencies
│   └── static/                # Legacy static files (optional)
├── frontend/                  # Enterprise Frontend
│   ├── login.html            # Admin console login (Wazuh/Nessus style)
│   ├── dashboard.html        # Enterprise dashboard
│   ├── enterprise.html       # Enterprise dashboard (alternative)
│   ├── css/
│   │   ├── login.css         # Admin login styles (dark theme)
│   │   ├── dashboard.css     # Enterprise dashboard styles
│   │   └── enterprise.css    # Enterprise design system
│   └── js/
│       ├── login.js          # Login/Register functionality
│       └── dashboard.js      # Dashboard interactivity
├── data/                      # Data files & logs
│   ├── *.csv                # User activity data
│   └── simulate_*.py        # Data generation scripts
├── models/                    # Trained ML models
│   ├── train.py             # Model training script
│   ├── isolation_forest.pkl
│   ├── oneclass_svm.pkl
│   └── autoencoder.pkl
├── features/                  # Feature engineering
├── gnn/                       # Graph neural network
├── explainability/            # SHAP/LIME explainers
├── requirements.txt           # Project dependencies
└── start_server.bat          # Windows server starter
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train ML Models (if not already trained)

```bash
cd models
python train.py
cd ..
```

### 3. Start the Backend Server

**Windows:**
```bash
start_server.bat
```

**Manual:**
```bash
cd backend
python app.py
```

The server will start at `http://localhost:5000`

### 4. Access the Application

Open your browser and go to: `http://localhost:5000`

## Demo Accounts

| Username | Password   | Role              |
|----------|------------|-------------------|
| admin    | admin123   | System Admin      |
| analyst  | analyst123 | Security Analyst  |
| soc      | soc123     | SOC Operator      |

## API Endpoints

### Authentication
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/register` - Register new user (enterprise)
- `GET /api/auth/me` - Get current user info

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/users` - Get all users with anomaly scores
- `GET /api/users/<user_id>` - Get user details

### Graph Analysis
- `GET /api/graph/nodes` - Get graph nodes (users)
- `GET /api/graph/edges` - Get graph edges (relationships)

### ML Prediction
- `POST /api/predict` - Run ML prediction on features

## Enterprise Features

### Admin Console (Login)
- **Dark theme** (Wazuh/Nessus inspired)
- **Login/Register tabs** - User registration support
- **Role-based access** - Admin, Analyst, SOC roles
- **Quick login chips** - Fast demo account access
- **Form validation** - Client-side validation
- **Error/Success messages** - User feedback

### Enterprise Dashboard
- **Two-panel layout** - Sidebar (220px) + Main content
- **Professional design system** - #185FA5 primary, 0.5px borders
- **KPI Cards** - Critical threats, High risk users, Monitored users, Avg anomaly score
- **Chart.js Visualizations** - Anomaly trend (line), Risk distribution (donut)
- **User Anomalies Table** - Risk badges, sorting, filtering, pagination
- **User Detail View** - Behavioral features, SHAP importance, model scores
- **Entity Graph** - High-risk nodes, flagged connections
- **Model Explain** - Accordion-style ML pipeline documentation
- **Real-time Alerts** - Critical/Warning notifications

## Design System

### Colors
- **Primary**: #185FA5 (blue)
- **Background**: #F5F7FA (light gray)
- **Card**: #FFFFFF (white)
- **Borders**: 0.5px #E2E8F0
- **Text Primary**: #111827
- **Text Secondary**: #6B7280
- **Risk Colors**: Critical (red), High (amber), Medium (purple), Low (green)

### Typography
- **Font**: Inter (Google Fonts)
- **Hierarchy**: Clear heading and body text separation

### Components
- **Border Radius**: 8px (elements), 12px (cards)
- **Spacing**: 20px page padding, 12-14px gap between cards
- **Tables**: Hover states, sortable headers, risk badges

## Technology Stack

- **Backend**: Flask, Flask-JWT-Extended, Flask-CORS, Werkzeug
- **ML**: scikit-learn (Isolation Forest, One-Class SVM, MLP/Autoencoder)
- **Data**: pandas, numpy, joblib
- **Graph**: NetworkX
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Chart.js 4.4.1
- **Icons**: Font Awesome 6.4.2
- **Font**: Inter

## Routes

- `/` - Admin Login (redirects if authenticated)
- `/enterprise` - Enterprise Dashboard (JWT required)
- `/dashboard` - Alternative dashboard (JWT required)

## Security Notes

- JWT tokens expire after 8 hours
- Passwords are hashed with Werkzeug
- All API endpoints (except login/register) require authentication
- In production, change `JWT_SECRET_KEY` and use HTTPS

## Development

To run in development mode with auto-reload:

```bash
cd backend
FLASK_ENV=development python app.py
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT License
