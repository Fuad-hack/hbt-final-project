/**
 * Sentinel ITP Dashboard - Backend API Integration
 * FastAPI Backend Connection
 */

// API Configuration - Backend runs on port 5000
const API_BASE_URL = 'http://localhost:5000';

// State with API data
const apiState = {
  currentUser: null,
  token: localStorage.getItem('access_token'),
  dashboardStats: null,
  users: [],
  alerts: []
};

// ═════════════════════════════════════════════════════════════════
// AUTH FUNCTIONS
// ═════════════════════════════════════════════════════════════════

async function verifyToken(token) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.ok;
  } catch (error) {
    console.error('Token verification failed:', error);
    return false;
  }
}

function redirectToLogin() {
  localStorage.removeItem('access_token');
  window.location.href = '/login';
}

// Check auth on load
document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    redirectToLogin();
    return;
  }
  
  const valid = await verifyToken(token);
  if (!valid) {
    redirectToLogin();
    return;
  }
  
  // Load dashboard data
  await loadDashboardData();
});

// ═════════════════════════════════════════════════════════════════
// API FUNCTIONS
// ═════════════════════════════════════════════════════════════════

async function apiGet(endpoint) {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    if (response.status === 401) {
      redirectToLogin();
    }
    throw new Error(`API error: ${response.status}`);
  }
  
  return response.json();
}

// ═════════════════════════════════════════════════════════════════
// DASHBOARD DATA LOADING
// ═════════════════════════════════════════════════════════════════

async function loadDashboardData() {
  try {
    // Load user info
    const user = await apiGet('/api/auth/me');
    apiState.currentUser = user;
    updateUserProfile(user);
    
    // Load dashboard stats
    const stats = await apiGet('/api/dashboard/stats');
    apiState.dashboardStats = stats;
    updateDashboardStats(stats);
    
    // Load users
    const usersData = await apiGet('/api/users');
    apiState.users = usersData.users || [];
    populateUsersTable(apiState.users);
    
    // Load alerts
    const alertsData = await apiGet('/api/alerts');
    apiState.alerts = alertsData.alerts || [];
    updateAlertsBadge(alertsData.unread || 0);
    
  } catch (error) {
    console.error('Error loading dashboard data:', error);
  }
}

function updateUserProfile(user) {
  const userNameEl = document.querySelector('.user-name');
  const userRoleEl = document.querySelector('.user-role');
  const userAvatarEl = document.querySelector('.user-avatar');
  
  if (userNameEl) userNameEl.textContent = user.name || user.username;
  if (userRoleEl) userRoleEl.textContent = user.role || 'Security Analyst';
  if (userAvatarEl) {
    const initials = (user.name || user.username).split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    userAvatarEl.textContent = initials;
  }
}

function updateDashboardStats(stats) {
  // Update metric cards if they exist
  const criticalEl = document.getElementById('mc-critical');
  const avgEl = document.getElementById('mc-avg');
  const redteamEl = document.getElementById('mc-redteam');
  const usersEl = document.getElementById('user-count');
  
  if (criticalEl) criticalEl.textContent = stats.critical_threats || 0;
  if (avgEl) avgEl.textContent = (stats.avg_anomaly_score || 0).toFixed(2);
  if (redteamEl) redteamEl.textContent = stats.red_team_count || 0;
  if (usersEl) usersEl.textContent = stats.users_monitored || 247;
}

function populateUsersTable(users) {
  // Find the users table
  const tableBody = document.querySelector('.anomaly-table tbody');
  if (!tableBody) return;
  
  // Clear existing rows
  tableBody.innerHTML = '';
  
  // Add user rows
  users.slice(0, 10).forEach(user => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${user.user_id || user.id}</td>
      <td>${user.full_name || user.username}</td>
      <td>${user.department || 'N/A'}</td>
      <td><span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">${user.is_active ? 'Active' : 'Inactive'}</span></td>
      <td>${user.role || 'analyst'}</td>
    `;
    tableBody.appendChild(row);
  });
}

function updateAlertsBadge(count) {
  const badge = document.querySelector('.nav-badge');
  if (badge) {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
  }
}

// Logout function
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}

// Make logout available globally
window.logout = logout;
window.loadDashboardData = loadDashboardData;
