#!/usr/bin/env python3
"""
ITDT FastAPI Server Startup Script
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║        ITDT - Insider Threat Detection System                ║
║                  FastAPI Backend v1.0                        ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting server...

📚 API Documentation: http://localhost:5000/api/docs
🔴 ReDoc Documentation: http://localhost:5000/api/redoc
💚 Health Check: http://localhost:5000/healthz
🌐 Dashboard: http://localhost:5000

Press Ctrl+C to stop
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
