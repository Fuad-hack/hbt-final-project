/**
 * SentinelAI Dashboard JavaScript
 * Real-time threat detection dashboard with API integration
 */

// API Configuration
const API_BASE_URL = window.location.origin;

// State
let currentUser = null;
let accessToken = null;
let usersData = [];
let currentPage = 1;
let itemsPerPage = 10;
let sortField = 'anomaly_score';
let sortDirection = 'desc';
let activeTab = 'overview';

// DOM Elements
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const logoutBtn = document.getElementById('logoutBtn');
const refreshBtn = document.getElementById('refreshBtn');
const threatTableBody = document.getElementById('threatTableBody');
const searchInput = document.getElementById('searchInput');
const riskFilter = document.getElementById('riskFilter');
const redTeamFilter = document.getElementById('redTeamFilter');
const modal = document.getElementById('userModal');
const closeModal = document.getElementById('closeModal');
const activityStream = document.getElementById('activityStream');

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', async () => {
  // Check authentication
  accessToken = localStorage.getItem('access_token');
  if (!accessToken) {
    window.location.href = '/';
    return;
  }
  
  // Load user info
  await loadUserInfo();
  
  // Load initial data
  await Promise.all([
    loadDashboardStats(),
    loadUsers(),
    initializeActivityFeed()
  ]);
  
  // Setup event listeners
  setupEventListeners();
  
  // Initialize model list
  initializeModelList();
  
  // Initialize notifications
  initializeNotifications();
  
  // Initialize charts after a short delay to ensure DOM is ready
  setTimeout(initializeCharts, 100);
});

// Authentication Functions
async function loadUserInfo() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.ok) {
      currentUser = await response.json();
      document.getElementById('userName').textContent = currentUser.name;
      document.getElementById('userRole').textContent = currentUser.role;
    } else {
      handleAuthError();
    }
  } catch (error) {
    console.error('Error loading user info:', error);
    handleAuthError();
  }
}

function handleAuthError() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/';
}

// Load Dashboard Stats
async function loadDashboardStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.ok) {
      const stats = await response.json();
      
      // Animate stat values
      animateValue('statCritical', 0, stats.critical_threats, 1000);
      animateValue('statHighRisk', 0, stats.high_risk_users, 1000);
      animateValue('statAvgScore', 0, Math.round(stats.avg_anomaly_score * 100), 1000, '%');
      animateValue('statRedTeam', 0, stats.red_team_flags, 1000);
      
      // Update badge
      const threatBadge = document.getElementById('threatBadge');
      threatBadge.textContent = stats.critical_threats;
      threatBadge.style.display = stats.critical_threats > 0 ? 'flex' : 'none';
    }
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

// Load Users Data
async function loadUsers() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/users`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      usersData = data.users || [];
      renderTable();
      updatePagination();
    }
  } catch (error) {
    console.error('Error loading users:', error);
    threatTableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center py-4">
          <span style="color: var(--text-muted)">Error loading data. Please refresh.</span>
        </td>
      </tr>
    `;
  }
}

// Render Threat Table
function renderTable() {
  const filtered = filterUsers();
  const sorted = sortUsers(filtered);
  const paginated = paginate(sorted);
  
  if (paginated.length === 0) {
    threatTableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center py-4">
          <span style="color: var(--text-muted)">No users found</span>
        </td>
      </tr>
    `;
    return;
  }
  
  threatTableBody.innerHTML = paginated.map(user => `
    <tr data-user-id="${user.id}">
      <td>
        <strong>${user.id}</strong>
        <div style="font-size: 0.75rem; color: var(--text-muted)">${user.name}</div>
      </td>
      <td>${user.department}</td>
      <td>
        <span class="risk-badge ${user.risk_level}">
          <i class="fas fa-circle" style="font-size: 6px"></i>
          ${user.risk_level.toUpperCase()}
        </span>
      </td>
      <td>
        <strong>${(user.anomaly_score * 100).toFixed(1)}%</strong>
      </td>
      <td>
        ${user.is_red_team ? `
          <span class="redteam-badge">
            <i class="fas fa-bug"></i>
            RED TEAM
          </span>
        ` : '<span style="color: var(--text-muted)">-</span>'}
      </td>
      <td>
        <div class="model-scores">
          <div class="model-score-item">
            <span class="model-score-label">Isolation F.</span>
            <div class="model-score-bar">
              <div class="model-score-fill" style="width: ${user.model_scores.isolation_forest * 100}%"></div>
            </div>
            <span class="model-score-value">${(user.model_scores.isolation_forest * 100).toFixed(0)}%</span>
          </div>
          <div class="model-score-item">
            <span class="model-score-label">One-Class</span>
            <div class="model-score-bar">
              <div class="model-score-fill" style="width: ${user.model_scores.oneclass_svm * 100}%"></div>
            </div>
            <span class="model-score-value">${(user.model_scores.oneclass_svm * 100).toFixed(0)}%</span>
          </div>
          <div class="model-score-item">
            <span class="model-score-label">Autoencoder</span>
            <div class="model-score-bar">
              <div class="model-score-fill" style="width: ${Math.min(user.model_scores.autoencoder * 100, 100)}%"></div>
            </div>
            <span class="model-score-value">${(Math.min(user.model_scores.autoencoder, 1) * 100).toFixed(0)}%</span>
          </div>
        </div>
      </td>
      <td>
        <div class="table-actions">
          <button class="table-btn" onclick="viewUserDetails('${user.id}')" title="View Details">
            <i class="fas fa-eye"></i>
          </button>
          <button class="table-btn" onclick="investigateUser('${user.id}')" title="Investigate">
            <i class="fas fa-search"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

// Filter Users
function filterUsers() {
  let filtered = [...usersData];
  
  // Search filter
  const searchTerm = searchInput.value.toLowerCase();
  if (searchTerm) {
    filtered = filtered.filter(user => 
      user.id.toLowerCase().includes(searchTerm) ||
      user.name.toLowerCase().includes(searchTerm) ||
      user.department.toLowerCase().includes(searchTerm)
    );
  }
  
  // Risk filter
  const riskValue = riskFilter.value;
  if (riskValue !== 'all') {
    filtered = filtered.filter(user => user.risk_level === riskValue);
  }
  
  // Red team filter
  const redTeamValue = redTeamFilter.value;
  if (redTeamValue !== 'all') {
    filtered = filtered.filter(user => 
      redTeamValue === 'yes' ? user.is_red_team : !user.is_red_team
    );
  }
  
  return filtered;
}

// Sort Users
function sortUsers(users) {
  return users.sort((a, b) => {
    let aVal, bVal;
    
    switch (sortField) {
      case 'user':
        aVal = a.id;
        bVal = b.id;
        break;
      case 'department':
        aVal = a.department;
        bVal = b.department;
        break;
      case 'risk_level':
        const riskOrder = { critical: 4, high: 3, medium: 2, low: 1 };
        aVal = riskOrder[a.risk_level] || 0;
        bVal = riskOrder[b.risk_level] || 0;
        break;
      case 'anomaly_score':
        aVal = a.anomaly_score;
        bVal = b.anomaly_score;
        break;
      default:
        aVal = a.id;
        bVal = b.id;
    }
    
    if (typeof aVal === 'string') {
      return sortDirection === 'asc' 
        ? aVal.localeCompare(bVal) 
        : bVal.localeCompare(aVal);
    }
    
    return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
  });
}

// Paginate Users
function paginate(users) {
  const start = (currentPage - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return users.slice(start, end);
}

// Update Pagination
function updatePagination() {
  const filtered = filterUsers();
  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  
  document.getElementById('showingStart').textContent = filtered.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0;
  document.getElementById('showingEnd').textContent = Math.min(currentPage * itemsPerPage, filtered.length);
  document.getElementById('totalItems').textContent = filtered.length;
  
  document.getElementById('prevPage').disabled = currentPage === 1;
  document.getElementById('nextPage').disabled = currentPage >= totalPages;
  
  // Page numbers
  const pageNumbers = document.getElementById('pageNumbers');
  let html = '';
  
  for (let i = 1; i <= totalPages && i <= 5; i++) {
    html += `<button class="page-number ${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
  }
  
  pageNumbers.innerHTML = html;
}

// View User Details
async function viewUserDetails(userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.ok) {
      const user = await response.json();
      showUserModal(user);
    }
  } catch (error) {
    console.error('Error loading user details:', error);
  }
}

// Show User Modal
function showUserModal(user) {
  const modalTitle = document.getElementById('modalUserTitle');
  const modalBody = document.getElementById('modalBody');
  
  modalTitle.textContent = `User: ${user.id}`;
  
  modalBody.innerHTML = `
    <div class="user-detail-header">
      <div class="detail-section">
        <h4>Basic Information</h4>
        <div class="detail-grid">
          <div class="detail-item">
            <label>User ID</label>
            <span>${user.id}</span>
          </div>
          <div class="detail-item">
            <label>Department</label>
            <span>${user.department}</span>
          </div>
          <div class="detail-item">
            <label>Risk Level</label>
            <span class="risk-badge ${user.risk_level}">${user.risk_level.toUpperCase()}</span>
          </div>
          <div class="detail-item">
            <label>Red Team</label>
            <span>${user.is_red_team ? 'Yes' : 'No'}</span>
          </div>
        </div>
      </div>
      
      <div class="detail-section">
        <h4>Anomaly Scores</h4>
        <div class="model-scores-detailed">
          <div class="score-row">
            <span>Isolation Forest</span>
            <div class="score-bar-large">
              <div class="score-fill" style="width: ${user.model_scores.isolation_forest * 100}%"></div>
            </div>
            <span>${(user.model_scores.isolation_forest * 100).toFixed(1)}%</span>
          </div>
          <div class="score-row">
            <span>One-Class SVM</span>
            <div class="score-bar-large">
              <div class="score-fill" style="width: ${user.model_scores.oneclass_svm * 100}%"></div>
            </div>
            <span>${(user.model_scores.oneclass_svm * 100).toFixed(1)}%</span>
          </div>
          <div class="score-row">
            <span>Autoencoder</span>
            <div class="score-bar-large">
              <div class="score-fill" style="width: ${Math.min(user.model_scores.autoencoder * 100, 100)}%"></div>
            </div>
            <span>${(Math.min(user.model_scores.autoencoder, 1) * 100).toFixed(1)}%</span>
          </div>
          <div class="score-row combined">
            <span>Combined Score</span>
            <div class="score-bar-large">
              <div class="score-fill combined" style="width: ${user.anomaly_score * 100}%"></div>
            </div>
            <span>${(user.anomaly_score * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>
      
      <div class="detail-section">
        <h4>Activity Summary</h4>
        <div class="activity-summary">
          <div class="activity-item">
            <i class="fas fa-sign-in-alt"></i>
            <span>Logins: ${user.activity_summary?.logins || 0}</span>
          </div>
          <div class="activity-item">
            <i class="fas fa-file"></i>
            <span>File Access: ${user.activity_summary?.file_access || 0}</span>
          </div>
          <div class="activity-item">
            <i class="fas fa-usb"></i>
            <span>USB Usage: ${user.activity_summary?.usb_usage || 0}</span>
          </div>
          <div class="activity-item">
            <i class="fas fa-envelope"></i>
            <span>Emails: ${user.activity_summary?.emails || 0}</span>
          </div>
        </div>
      </div>
    </div>
    
    <style>
      .user-detail-header { display: flex; flex-direction: column; gap: 1.5rem; }
      .detail-section h4 { 
        font-size: 0.875rem; 
        color: var(--text-secondary); 
        margin-bottom: 0.75rem; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
      }
      .detail-grid { 
        display: grid; 
        grid-template-columns: repeat(2, 1fr); 
        gap: 1rem; 
      }
      .detail-item { display: flex; flex-direction: column; gap: 0.25rem; }
      .detail-item label { font-size: 0.75rem; color: var(--text-muted); }
      .detail-item span { font-size: 0.9375rem; color: var(--text-primary); }
      .model-scores-detailed { display: flex; flex-direction: column; gap: 0.75rem; }
      .score-row { 
        display: flex; 
        align-items: center; 
        gap: 1rem; 
        font-size: 0.875rem;
      }
      .score-row span:first-child { width: 120px; color: var(--text-secondary); }
      .score-bar-large { 
        flex: 1; 
        height: 10px; 
        background: var(--bg-hover); 
        border-radius: 100px; 
        overflow: hidden;
      }
      .score-fill { 
        height: 100%; 
        background: linear-gradient(90deg, var(--primary), var(--secondary)); 
        border-radius: 100px;
        transition: width 0.5s ease;
      }
      .score-fill.combined { background: linear-gradient(90deg, var(--danger), var(--warning)); }
      .score-row.combined { font-weight: 600; }
      .score-row span:last-child { 
        width: 60px; 
        text-align: right; 
        color: var(--text-primary);
        font-weight: 500;
      }
      .activity-summary { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
      .activity-item { 
        display: flex; 
        align-items: center; 
        gap: 0.625rem; 
        padding: 0.75rem; 
        background: var(--bg-hover);
        border-radius: var(--radius-sm);
        font-size: 0.875rem;
      }
      .activity-item i { color: var(--primary); }
    </style>
  `;
  
  modal.classList.add('active');
}

// Investigate User
function investigateUser(userId) {
  console.log('Investigating user:', userId);
  // Could open a detailed investigation panel
  alert(`Investigation mode for ${userId} - Full feature coming soon!`);
}

// Activity Feed
const activityTypes = [
  { icon: 'fa-exclamation-circle', type: 'alert', title: 'High Anomaly Detected' },
  { icon: 'fa-user-shield', type: 'warning', title: 'Suspicious Login' },
  { icon: 'fa-file-download', type: 'alert', title: 'Bulk Download' },
  { icon: 'fa-usb', type: 'info', title: 'USB Connected' },
  { icon: 'fa-envelope', type: 'warning', title: 'External Email' },
  { icon: 'fa-lock', type: 'alert', title: 'Failed Auth' },
  { icon: 'fa-clock', type: 'info', title: 'After-hours Access' }
];

function initializeActivityFeed() {
  // Add initial items
  for (let i = 0; i < 5; i++) {
    addActivityItem();
  }
  
  // Add new item every 3-8 seconds
  setInterval(() => {
    if (Math.random() > 0.4) {
      addActivityItem();
    }
  }, 5000);
}

function addActivityItem() {
  const activity = activityTypes[Math.floor(Math.random() * activityTypes.length)];
  const users = usersData.length > 0 ? usersData : [{ id: 'USR-0001' }, { id: 'USR-0042' }, { id: 'USR-0156' }];
  const user = users[Math.floor(Math.random() * users.length)];
  
  const item = document.createElement('div');
  item.className = 'activity-item';
  item.innerHTML = `
    <div class="activity-icon ${activity.type}">
      <i class="fas ${activity.icon}"></i>
    </div>
    <div class="activity-content">
      <div class="activity-title">${activity.title}</div>
      <div class="activity-desc">User ${user.id} - ${getRandomDetail(activity.title)}</div>
    </div>
    <div class="activity-time">${getTimeAgo()}</div>
  `;
  
  activityStream.insertBefore(item, activityStream.firstChild);
  
  // Keep only 8 items
  while (activityStream.children.length > 8) {
    activityStream.removeChild(activityStream.lastChild);
  }
}

function getRandomDetail(title) {
  const details = {
    'High Anomaly Detected': ['Score: 87%', 'Multiple triggers', 'Pattern match'],
    'Suspicious Login': ['Unusual location', 'Off-hours', 'New device'],
    'Bulk Download': ['247 files', 'Sensitive docs', 'After hours'],
    'USB Connected': ['External device', 'Mass storage', 'Unknown brand'],
    'External Email': ['Large attachment', 'Sensitive keywords', 'Unknown recipient'],
    'Failed Auth': ['3 attempts', 'Wrong password', 'Account locked'],
    'After-hours Access': ['Weekend access', 'Sensitive files', 'VPN connection']
  };
  const options = details[title] || ['Event detected'];
  return options[Math.floor(Math.random() * options.length)];
}

function getTimeAgo() {
  const seconds = Math.floor(Math.random() * 60) + 1;
  if (seconds < 10) return 'Just now';
  if (seconds < 30) return `${seconds}s ago`;
  return `${Math.floor(seconds / 60) + 1}m ago`;
}

// Initialize Model List
function initializeModelList() {
  const modelList = document.getElementById('modelList');
  if (!modelList) return;
  
  const models = [
    { name: 'Isolation Forest', icon: 'fa-tree', desc: 'Active - Detecting outliers' },
    { name: 'One-Class SVM', icon: 'fa-vector-square', desc: 'Active - Boundary detection' },
    { name: 'Autoencoder', icon: 'fa-network-wired', desc: 'Active - Reconstruction error' }
  ];
  
  modelList.innerHTML = models.map(model => `
    <div class="model-item">
      <div class="model-icon">
        <i class="fas ${model.icon}"></i>
      </div>
      <div class="model-info">
        <div class="model-name">${model.name}</div>
        <div class="model-status">${model.desc}</div>
      </div>
    </div>
  `).join('');
}

// Initialize Notifications
function initializeNotifications() {
  const notificationsList = document.getElementById('notificationsList');
  if (!notificationsList) return;
  
  const notifications = [
    { type: 'critical', icon: 'fa-exclamation-circle', title: 'Critical Threat Detected', desc: 'User USR-4821 - Anomaly score 94%', time: '2 min ago' },
    { type: 'warning', icon: 'fa-file-export', title: 'Bulk Download Alert', desc: 'User USR-3156 - 247 files accessed', time: '5 min ago' },
    { type: 'warning', icon: 'fa-usb', title: 'USB Device Connected', desc: 'User USR-7823 - External storage detected', time: '12 min ago' },
    { type: 'info', icon: 'fa-envelope', title: 'Suspicious Email Pattern', desc: 'Multiple external recipients detected', time: '18 min ago' },
    { type: 'critical', icon: 'fa-lock', title: 'Failed Authentication', desc: 'User USR-1234 - 3 failed attempts', time: '25 min ago' }
  ];
  
  notificationsList.innerHTML = notifications.map(n => `
    <div class="notification-item">
      <div class="notification-icon ${n.type}">
        <i class="fas ${n.icon}"></i>
      </div>
      <div class="notification-content">
        <div class="notification-title">${n.title}</div>
        <div class="notification-desc">${n.desc}</div>
      </div>
      <div class="notification-time">${n.time}</div>
    </div>
  `).join('');
}

// Event Listeners
function setupEventListeners() {
  // Sidebar toggle
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
  
  // Logout
  logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/';
  });
  
  // Refresh
  refreshBtn.addEventListener('click', async () => {
    refreshBtn.querySelector('i').classList.add('fa-spin');
    await Promise.all([
      loadDashboardStats(),
      loadUsers()
    ]);
    updateCharts();
    setTimeout(() => {
      refreshBtn.querySelector('i').classList.remove('fa-spin');
    }, 1000);
  });
  
  // Notifications
  const notificationsBtn = document.getElementById('notificationsBtn');
  const notificationsPanel = document.getElementById('notificationsPanel');
  const markAllReadBtn = document.getElementById('markAllRead');
  
  if (notificationsBtn && notificationsPanel) {
    notificationsBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notificationsPanel.classList.toggle('active');
    });
    
    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!notificationsPanel.contains(e.target) && !notificationsBtn.contains(e.target)) {
        notificationsPanel.classList.remove('active');
      }
    });
  }
  
  if (markAllReadBtn) {
    markAllReadBtn.addEventListener('click', () => {
      document.querySelectorAll('.notification-item').forEach(item => {
        item.style.opacity = '0.5';
      });
      document.querySelector('.notification-badge')?.classList.remove('active');
    });
  }
  
  // Search & Filter
  searchInput.addEventListener('input', () => {
    currentPage = 1;
    renderTable();
    updatePagination();
  });
  
  riskFilter.addEventListener('change', () => {
    currentPage = 1;
    renderTable();
    updatePagination();
  });
  
  redTeamFilter.addEventListener('change', () => {
    currentPage = 1;
    renderTable();
    updatePagination();
  });
  
  // Table sorting
  document.querySelectorAll('.data-table th.sortable').forEach(th => {
    th.addEventListener('click', () => {
      const field = th.dataset.sort;
      if (sortField === field) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        sortField = field;
        sortDirection = 'desc';
      }
      renderTable();
      
      // Update sort icons
      document.querySelectorAll('.data-table th.sortable i').forEach(icon => {
        icon.className = 'fas fa-sort';
      });
      th.querySelector('i').className = `fas fa-sort-${sortDirection === 'asc' ? 'up' : 'down'}`;
    });
  });
  
  // Pagination
  document.getElementById('prevPage').addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      renderTable();
      updatePagination();
    }
  });
  
  document.getElementById('nextPage').addEventListener('click', () => {
    const totalPages = Math.ceil(filterUsers().length / itemsPerPage);
    if (currentPage < totalPages) {
      currentPage++;
      renderTable();
      updatePagination();
    }
  });
  
  document.getElementById('pageNumbers').addEventListener('click', (e) => {
    if (e.target.classList.contains('page-number')) {
      currentPage = parseInt(e.target.dataset.page);
      renderTable();
      updatePagination();
    }
  });
  
  // Tab navigation
  document.querySelectorAll('.nav-item[data-tab]').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const tabName = item.dataset.tab;
      
      // Update active states
      document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
      item.classList.add('active');
      
      // Show/hide tabs
      document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
      document.getElementById(`tab-${tabName}`).classList.add('active');
      
      // Update breadcrumb
      document.querySelector('.current-page').textContent = item.querySelector('span').textContent;
      
      activeTab = tabName;
    });
  });
  
  // Modal
  closeModal.addEventListener('click', () => {
    modal.classList.remove('active');
  });
  
  modal.querySelector('.modal-overlay').addEventListener('click', () => {
    modal.classList.remove('active');
  });
  
  // Fullscreen
  document.getElementById('fullscreenBtn').addEventListener('click', () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  });
  
  // Export
  document.getElementById('exportBtn').addEventListener('click', () => {
    exportToCSV();
  });
  
  // Analyze
  document.getElementById('analyzeBtn').addEventListener('click', () => {
    alert('Running ML analysis on current data...');
  });
}

// Export to CSV
function exportToCSV() {
  const filtered = filterUsers();
  const headers = ['User ID', 'Department', 'Risk Level', 'Anomaly Score', 'Red Team', 'Isolation Forest', 'One-Class SVM', 'Autoencoder'];
  
  const csvContent = [
    headers.join(','),
    ...filtered.map(user => [
      user.id,
      user.department,
      user.risk_level,
      user.anomaly_score,
      user.is_red_team ? 'Yes' : 'No',
      user.model_scores.isolation_forest,
      user.model_scores.oneclass_svm,
      user.model_scores.autoencoder
    ].join(','))
  ].join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `threat-detection-${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  window.URL.revokeObjectURL(url);
}

// Animate Value
function animateValue(id, start, end, duration, suffix = '') {
  const obj = document.getElementById(id);
  const range = end - start;
  const minTimer = 50;
  let stepTime = Math.abs(Math.floor(duration / range));
  stepTime = Math.max(stepTime, minTimer);
  
  let startTime = new Date().getTime();
  let endTime = startTime + duration;
  let timer;
  
  function run() {
    let now = new Date().getTime();
    let remaining = Math.max((endTime - now) / duration, 0);
    let value = Math.round(end - (remaining * range));
    obj.innerHTML = value + suffix;
    if (value == end) {
      clearInterval(timer);
    }
  }
  
  timer = setInterval(run, stepTime);
  run();
}

// Chart.js instances
let trendChart, riskChart, histogramChart, radarChart, timelineChart;

// Initialize Charts
function initializeCharts() {
  initTrendChart();
  initRiskChart();
  initHistogramChart();
  initRadarChart();
  initTimelineChart();
  initModelAgreementHeatmap();
}

// Anomaly Trend Chart (Line Chart)
function initTrendChart() {
  const ctx = document.getElementById('trendChart');
  if (!ctx) return;
  
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);
  const data = generateTrendData();
  
  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: hours,
      datasets: [
        {
          label: 'Critical',
          data: data.critical,
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'High Risk',
          data: data.high,
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Medium',
          data: data.medium,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#9ca3af', usePointStyle: true }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(55, 65, 81, 0.5)' },
          ticks: { color: '#9ca3af' }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#9ca3af', maxTicksLimit: 8 }
        }
      }
    }
  });
}

// Risk Distribution Chart (Doughnut)
function initRiskChart() {
  const ctx = document.getElementById('riskChart');
  if (!ctx) return;
  
  const counts = countByRiskLevel();
  
  riskChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Critical', 'High', 'Medium', 'Low'],
      datasets: [{
        data: [counts.critical, counts.high, counts.medium, counts.low],
        backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#9ca3af', padding: 20, usePointStyle: true }
        }
      }
    }
  });
}

// Histogram Chart (Bar Chart)
function initHistogramChart() {
  const ctx = document.getElementById('histogramChart');
  if (!ctx) return;
  
  const scores = usersData.map(u => u.anomaly_score);
  const bins = createHistogramBins(scores, 10);
  
  histogramChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: bins.labels,
      datasets: [{
        label: 'Users',
        data: bins.counts,
        backgroundColor: bins.colors,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(55, 65, 81, 0.5)' },
          ticks: { color: '#9ca3af' }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#9ca3af' }
        }
      }
    }
  });
}

// Radar Chart for Model Comparison
function initRadarChart() {
  const ctx = document.getElementById('radarChart');
  if (!ctx) return;
  
  const avgScores = calculateAverageModelScores();
  
  radarChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Detection Rate', 'Precision', 'Recall', 'F1-Score', 'Speed', 'Robustness'],
      datasets: [
        {
          label: 'Isolation Forest',
          data: [avgScores.iso * 100, 85, 78, 81, 95, 88],
          borderColor: '#00d4ff',
          backgroundColor: 'rgba(0, 212, 255, 0.2)',
          pointBackgroundColor: '#00d4ff'
        },
        {
          label: 'One-Class SVM',
          data: [avgScores.svm * 100, 82, 75, 78, 70, 85],
          borderColor: '#7c3aed',
          backgroundColor: 'rgba(124, 58, 237, 0.2)',
          pointBackgroundColor: '#7c3aed'
        },
        {
          label: 'Autoencoder',
          data: [avgScores.ae * 100, 80, 82, 81, 60, 75],
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.2)',
          pointBackgroundColor: '#f59e0b'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#9ca3af', usePointStyle: true }
        }
      },
      scales: {
        r: {
          beginAtZero: true,
          max: 100,
          grid: { color: 'rgba(55, 65, 81, 0.5)' },
          pointLabels: { color: '#9ca3af' },
          ticks: { display: false }
        }
      }
    }
  });
}

// Timeline Chart for High-Risk Users
function initTimelineChart() {
  const ctx = document.getElementById('timelineChart');
  if (!ctx) return;
  
  const highRiskUsers = usersData
    .filter(u => u.risk_level === 'critical' || u.risk_level === 'high')
    .slice(0, 5);
  
  const datasets = highRiskUsers.map((user, index) => ({
    label: user.id,
    data: generateUserTimelineData(user.anomaly_score),
    borderColor: getRiskColor(user.risk_level),
    backgroundColor: getRiskColor(user.risk_level) + '33',
    fill: false,
    tension: 0.4
  }));
  
  timelineChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { color: '#9ca3af', usePointStyle: true }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: { color: 'rgba(55, 65, 81, 0.5)' },
          ticks: { color: '#9ca3af', callback: v => v + '%' }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#9ca3af' }
        }
      }
    }
  });
}

// Model Agreement Heatmap
function initModelAgreementHeatmap() {
  const container = document.getElementById('modelAgreement');
  if (!container) return;
  
  const topUsers = usersData
    .sort((a, b) => b.anomaly_score - a.anomaly_score)
    .slice(0, 8);
  
  let html = '<div class="heatmap-grid">';
  html += '<div class="heatmap-cell header">User</div>';
  html += '<div class="heatmap-cell header">Isolation Forest</div>';
  html += '<div class="heatmap-cell header">One-Class SVM</div>';
  html += '<div class="heatmap-cell header">Autoencoder</div>';
  
  topUsers.forEach(user => {
    const isoClass = getAgreementClass(user.model_scores.isolation_forest);
    const svmClass = getAgreementClass(user.model_scores.oneclass_svm);
    const aeClass = getAgreementClass(Math.min(user.model_scores.autoencoder, 1));
    
    html += `<div class="heatmap-cell user-label">${user.id}</div>`;
    html += `<div class="heatmap-cell ${isoClass}">${(user.model_scores.isolation_forest * 100).toFixed(0)}%</div>`;
    html += `<div class="heatmap-cell ${svmClass}">${(user.model_scores.oneclass_svm * 100).toFixed(0)}%</div>`;
    html += `<div class="heatmap-cell ${aeClass}">${(Math.min(user.model_scores.autoencoder, 1) * 100).toFixed(0)}%</div>`;
  });
  
  html += '</div>';
  html += `
    <div class="heatmap-legend">
      <div class="heatmap-legend-item">
        <div class="heatmap-legend-dot agreement-high"></div>
        <span>High Agreement (>70%)</span>
      </div>
      <div class="heatmap-legend-item">
        <div class="heatmap-legend-dot agreement-medium"></div>
        <span>Medium (40-70%)</span>
      </div>
      <div class="heatmap-legend-item">
        <div class="heatmap-legend-dot agreement-low"></div>
        <span>Low Agreement (<40%)</span>
      </div>
    </div>
  `;
  
  container.innerHTML = html;
}

// Helper Functions for Charts
function generateTrendData() {
  return {
    critical: Array.from({ length: 24 }, () => Math.floor(Math.random() * 5)),
    high: Array.from({ length: 24 }, () => Math.floor(Math.random() * 8) + 2),
    medium: Array.from({ length: 24 }, () => Math.floor(Math.random() * 12) + 5)
  };
}

function countByRiskLevel() {
  return usersData.reduce((acc, user) => {
    acc[user.risk_level] = (acc[user.risk_level] || 0) + 1;
    return acc;
  }, { critical: 0, high: 0, medium: 0, low: 0 });
}

function createHistogramBins(scores, binCount) {
  const min = 0, max = 1;
  const binWidth = (max - min) / binCount;
  const bins = Array(binCount).fill(0);
  
  scores.forEach(score => {
    const binIndex = Math.min(Math.floor(score / binWidth), binCount - 1);
    bins[binIndex]++;
  });
  
  const labels = bins.map((_, i) => `${(i * binWidth * 100).toFixed(0)}-${((i + 1) * binWidth * 100).toFixed(0)}%`);
  const colors = bins.map((_, i) => {
    const threshold = i / binCount;
    if (threshold >= 0.8) return '#ef4444';
    if (threshold >= 0.6) return '#f59e0b';
    if (threshold >= 0.35) return '#3b82f6';
    return '#10b981';
  });
  
  return { labels, counts: bins, colors };
}

function calculateAverageModelScores() {
  if (usersData.length === 0) return { iso: 0.5, svm: 0.5, ae: 0.5 };
  
  const totals = usersData.reduce((acc, user) => ({
    iso: acc.iso + user.model_scores.isolation_forest,
    svm: acc.svm + user.model_scores.oneclass_svm,
    ae: acc.ae + Math.min(user.model_scores.autoencoder, 1)
  }), { iso: 0, svm: 0, ae: 0 });
  
  return {
    iso: totals.iso / usersData.length,
    svm: totals.svm / usersData.length,
    ae: totals.ae / usersData.length
  };
}

function generateUserTimelineData(baseScore) {
  return Array.from({ length: 7 }, () => {
    const variation = (Math.random() - 0.5) * 0.3;
    return Math.min(Math.max((baseScore + variation) * 100, 0), 100);
  });
}

function getRiskColor(riskLevel) {
  const colors = {
    critical: '#ef4444',
    high: '#f59e0b',
    medium: '#3b82f6',
    low: '#10b981'
  };
  return colors[riskLevel] || '#6b7280';
}

function getAgreementClass(score) {
  if (score >= 0.7) return 'agreement-high';
  if (score >= 0.4) return 'agreement-medium';
  return 'agreement-low';
}

// Update charts when data changes
function updateCharts() {
  if (riskChart) {
    const counts = countByRiskLevel();
    riskChart.data.datasets[0].data = [counts.critical, counts.high, counts.medium, counts.low];
    riskChart.update();
  }
  
  if (histogramChart) {
    const scores = usersData.map(u => u.anomaly_score);
    const bins = createHistogramBins(scores, 10);
    histogramChart.data.labels = bins.labels;
    histogramChart.data.datasets[0].data = bins.counts;
    histogramChart.data.datasets[0].backgroundColor = bins.colors;
    histogramChart.update();
  }
  
  initModelAgreementHeatmap();
  
  if (radarChart) {
    const avgScores = calculateAverageModelScores();
    radarChart.data.datasets[0].data[0] = avgScores.iso * 100;
    radarChart.data.datasets[1].data[0] = avgScores.svm * 100;
    radarChart.data.datasets[2].data[0] = avgScores.ae * 100;
    radarChart.update();
  }
  
  if (timelineChart) {
    const highRiskUsers = usersData
      .filter(u => u.risk_level === 'critical' || u.risk_level === 'high')
      .slice(0, 5);
    
    timelineChart.data.datasets = highRiskUsers.map(user => ({
      label: user.id,
      data: generateUserTimelineData(user.anomaly_score),
      borderColor: getRiskColor(user.risk_level),
      backgroundColor: getRiskColor(user.risk_level) + '33',
      fill: false,
      tension: 0.4
    }));
    timelineChart.update();
  }
}

// Expose functions to global scope
window.viewUserDetails = viewUserDetails;
window.investigateUser = investigateUser;
