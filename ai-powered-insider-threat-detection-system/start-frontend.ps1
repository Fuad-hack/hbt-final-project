#!/usr/bin/env pwsh
# Start Frontend Server on Port 3000

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║        ITDT Frontend Server - Port 3000                      ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

$frontendPath = Join-Path $PSScriptRoot "frontend"

if (!(Test-Path $frontendPath)) {
    Write-Error "Frontend directory not found: $frontendPath"
    exit 1
}

Write-Host "Starting frontend server on http://localhost:3000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

# Try Python HTTP server first
try {
    python -m http.server 3000 --directory $frontendPath
} catch {
    # Fallback to Node.js http-server if available
    try {
        npx http-server $frontendPath -p 3000
    } catch {
        Write-Error "Could not start server. Please install Python or Node.js"
        Write-Host "Alternative: python -m http.server 3000 --directory frontend"
    }
}
