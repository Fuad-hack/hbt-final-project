/**
 * Sentinel ITP Enterprise Dashboard
 * JavaScript for interactivity and data visualization
 */

// ═════════════════════════════════════════════════════════════════
// STATE
// ═════════════════════════════════════════════════════════════════
const state = {
  currentView: 'dashboard',
  users: [],
  alerts: [],
  charts: {}
};

// ═════════════════════════════════════════════════════════════════
// MOCK DATA
// ═════════════════════════════════════════════════════════════════
const mockUsers = [
  { id: 'USR-4821', name: 'Michael U.', dept: 'Engineering', risk: 'critical', score: 0.94, trigger: 'After-hours download', lastEvent: '2 min ago' },
  { id: 'USR-3156', name: 'Sarah C.', dept: 'Finance', risk: 'high', score: 0.87, trigger: 'Bulk file access', lastEvent: '15 min ago' },
  { id: 'USR-7823', name: 'David W.', dept: 'Sales', risk: 'high', score: 0.82, trigger: 'USB connection', lastEvent: '32 min ago' },
  { id: 'USR-1234', name: 'Emma L.', dept: 'HR', risk: 'medium', score: 0.68, trigger: 'External email', lastEvent: '1 hour ago' },
  { id: 'USR-5678', name: 'James R.', dept: 'IT', risk: 'medium', score: 0.61, trigger: 'Failed auth', lastEvent: '2 hours ago' },
  { id: 'USR-9012', name: 'Lisa M.', dept: 'Marketing', risk: 'low', score: 0.34, trigger: 'None', lastEvent: '3 hours ago' },
  { id: 'USR-3456', name: 'Robert K.', dept: 'Legal', risk: 'low', score: 0.28, trigger: 'None', lastEvent: '5 hours ago' }
];

// Generate 247 users for the full table
for (let i = 0; i < 240; i++) {
  const risks = ['critical', 'high', 'medium', 'low'];
  const depts = ['Engineering', 'Finance', 'Sales', 'HR', 'IT', 'Marketing', 'Legal', 'Operations'];
  const triggers = ['After-hours download', 'Bulk file access', 'USB connection', 'External email', 'Failed auth', 'None', 'None'];
  
  mockUsers.push({
    id: `USR-${1000 + i}`,
    name: `User ${i + 8}`,
    dept: depts[Math.floor(Math.random() * depts.length)],
    risk: risks[Math.floor(Math.random() * risks.length)],
    score: Math.round((Math.random() * 0.8 + 0.1) * 100) / 100,
    trigger: triggers[Math.floor(Math.random() * triggers.length)],
    lastEvent: `${Math.floor(Math.random() * 24) + 1} hours ago`
  });
}

// ═════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initCharts();
  populateTables();
  initAccordion();
  initSearch();
});

// ═════════════════════════════════════════════════════════════════
// NAVIGATION
// ═════════════════════════════════════════════════════════════════
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const views = document.querySelectorAll('.view');
  
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      
      const viewName = item.dataset.view;
      if (!viewName) return;
      
      // Update active nav
      navItems.forEach(nav => nav.classList.remove('active'));
      item.classList.add('active');
      
      // Update page title
      const pageTitle = document.querySelector('.page-title');
      const breadcrumb = document.querySelector('.breadcrumb');
      
      const titles = {
        'dashboard': ['Dashboard', 'Real-time threat monitoring & investigation'],
        'alerts': ['Alerts', 'Security alerts and notifications'],
        'user-anomalies': ['User Anomalies', 'Anomaly detection results'],
        'user-detail': ['User Detail', 'Investigation profile'],
        'entity-graph': ['Entity Graph', 'User relationship analysis'],
        'red-team': ['Red Team Logs', 'Simulated threat activities'],
        'model-explain': ['Model Explain', 'AI/ML system documentation'],
        'settings': ['Settings', 'System configuration']
      };
      
      if (titles[viewName]) {
        pageTitle.textContent = titles[viewName][0];
        breadcrumb.textContent = titles[viewName][1];
      }
      
      // Show view
      views.forEach(view => view.classList.remove('active'));
      const targetView = document.getElementById(`view-${viewName}`);
      if (targetView) {
        targetView.classList.add('active');
        state.currentView = viewName;
        
        // Refresh charts if needed
        if (viewName === 'dashboard') {
          refreshCharts();
        }
      }
    });
  });
}

// ═════════════════════════════════════════════════════════════════
// CHARTS
// ═════════════════════════════════════════════════════════════════
function initCharts() {
  initTrendChart();
  initRiskChart();
  initActivityChart();
}

function initTrendChart() {
  const ctx = document.getElementById('trendChart');
  if (!ctx) return;
  
  const days = Array.from({ length: 14 }, (_, i) => `Day ${i + 1}`);
  const data = days.map(() => Math.round((Math.random() * 0.4 + 0.4) * 100) / 100);
  
  state.charts.trend = new Chart(ctx, {
    type: 'line',
    data: {
      labels: days,
      datasets: [{
        label: 'Avg Anomaly Score',
        data: data,
        borderColor: '#185FA5',
        backgroundColor: 'rgba(24, 95, 165, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: '#185FA5'
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
          min: 0,
          max: 1,
          grid: { color: '#E2E8F0', drawBorder: false },
          ticks: { color: '#6B7280', font: { size: 11 } }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#6B7280', font: { size: 11 }, maxTicksLimit: 7 }
        }
      }
    }
  });
}

function initRiskChart() {
  const ctx = document.getElementById('riskChart');
  if (!ctx) return;
  
  const riskCounts = {
    critical: mockUsers.filter(u => u.risk === 'critical').length,
    high: mockUsers.filter(u => u.risk === 'high').length,
    medium: mockUsers.filter(u => u.risk === 'medium').length,
    low: mockUsers.filter(u => u.risk === 'low').length
  };
  
  state.charts.risk = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Critical', 'High', 'Medium', 'Low'],
      datasets: [{
        data: [riskCounts.critical, riskCounts.high, riskCounts.medium, riskCounts.low],
        backgroundColor: ['#DC2626', '#D97706', '#7C3AED', '#059669'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            usePointStyle: true,
            pointStyle: 'circle',
            padding: 15,
            font: { size: 12 }
          }
        }
      }
    }
  });
}

function initActivityChart() {
  const ctx = document.getElementById('activityChart');
  if (!ctx) return;
  
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  
  state.charts.activity = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: days,
      datasets: [{
        label: 'Activity Score',
        data: [45, 52, 48, 61, 55, 38, 42],
        backgroundColor: '#185FA5',
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: { color: '#E2E8F0', drawBorder: false },
          ticks: { color: '#6B7280', font: { size: 11 } }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#6B7280', font: { size: 11 } }
        }
      }
    }
  });
}

function refreshCharts() {
  Object.values(state.charts).forEach(chart => {
    if (chart) chart.update();
  });
}

// ═════════════════════════════════════════════════════════════════
// TABLES
// ═════════════════════════════════════════════════════════════════
function populateTables() {
  // Dashboard table (top 7 users)
  const dashboardBody = document.getElementById('usersTableBody');
  if (dashboardBody) {
    dashboardBody.innerHTML = mockUsers.slice(0, 7).map(user => createUserRow(user)).join('');
  }
  
  // Full users table
  const allUsersBody = document.getElementById('allUsersTableBody');
  if (allUsersBody) {
    allUsersBody.innerHTML = mockUsers.slice(0, 20).map(user => createUserRow(user, true)).join('');
  }
}

function createUserRow(user, includeActions = false) {
  const riskColors = {
    critical: { bg: '#FEE2E2', text: '#991B1B' },
    high: { bg: '#FEF3C7', text: '#92400E' },
    medium: { bg: '#EDE9FE', text: '#5B21B6' },
    low: { bg: '#D1FAE5', text: '#065F46' }
  };
  
  const riskStyle = riskColors[user.risk];
  
  let html = `
    <tr>
      <td><code>${user.id}</code></td>
      <td>${user.name}</td>
      <td>${user.dept}</td>
      <td>
        <span class="risk-badge ${user.risk}" style="background: ${riskStyle.bg}; color: ${riskStyle.text}">
          ${user.risk.charAt(0).toUpperCase() + user.risk.slice(1)}
        </span>
      </td>
      <td>
        <div class="score-cell">
          <span class="score-value">${user.score.toFixed(2)}</span>
          <div class="score-bar">
            <div class="score-bar-fill" style="width: ${user.score * 100}%; background: ${riskStyle.text}"></div>
          </div>
        </div>
      </td>
      <td>${user.trigger}</td>
      <td>${user.lastEvent}</td>
  `;
  
  if (includeActions) {
    html += `
      <td>
        <button class="btn btn-text" onclick="viewUserDetail('${user.id}')">
          <i class="fas fa-eye"></i> View
        </button>
      </td>
    `;
  }
  
  html += '</tr>';
  return html;
}

function viewUserDetail(userId) {
  // Switch to user detail view
  document.querySelector('[data-view="user-detail"]').click();
  
  // Update user detail with this user's data
  const user = mockUsers.find(u => u.id === userId) || mockUsers[0];
  
  document.querySelector('.user-hero-info h2').textContent = user.name;
  document.querySelector('.user-dept').textContent = user.dept;
  document.querySelector('.user-score .score-value').textContent = user.score.toFixed(2);
  document.querySelector('.risk-badge').textContent = user.risk.charAt(0).toUpperCase() + user.risk.slice(1);
  document.querySelector('.risk-badge').className = `risk-badge ${user.risk}`;
}

// ═════════════════════════════════════════════════════════════════
// ACCORDION
// ═════════════════════════════════════════════════════════════════
function initAccordion() {
  const accordionHeaders = document.querySelectorAll('.accordion-header');
  
  accordionHeaders.forEach(header => {
    header.addEventListener('click', () => {
      const item = header.parentElement;
      const isOpen = item.classList.contains('open');
      
      // Close all
      document.querySelectorAll('.accordion-item').forEach(i => i.classList.remove('open'));
      
      // Open clicked if wasn't open
      if (!isOpen) {
        item.classList.add('open');
      }
    });
  });
  
  // Open first by default
  const firstItem = document.querySelector('.accordion-item');
  if (firstItem) firstItem.classList.add('open');
}

// ═════════════════════════════════════════════════════════════════
// SEARCH & FILTER
// ═════════════════════════════════════════════════════════════════
function initSearch() {
  const searchInput = document.querySelector('.search-box input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      filterTable(query);
    });
  }
}

function filterTable(query) {
  const rows = document.querySelectorAll('#allUsersTableBody tr');
  
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(query) ? '' : 'none';
  });
}

// ═════════════════════════════════════════════════════════════════
// BUTTON ACTIONS
// ═════════════════════════════════════════════════════════════════
// Export button
document.addEventListener('click', (e) => {
  if (e.target.closest('.btn')?.textContent.includes('Export')) {
    exportToCSV();
  }
});

function exportToCSV() {
  const headers = ['User ID', 'Name', 'Department', 'Risk Level', 'Anomaly Score', 'Top Trigger', 'Last Event'];
  const csvContent = [
    headers.join(','),
    ...mockUsers.map(u => [u.id, u.name, u.dept, u.risk, u.score, u.trigger, u.lastEvent].join(','))
  ].join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `sentinel-itp-export-${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  window.URL.revokeObjectURL(url);
}

// Run Scan button
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn');
  if (btn?.textContent.includes('Run Scan')) {
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scanning...';
    btn.disabled = true;
    
    setTimeout(() => {
      btn.innerHTML = '<i class="fas fa-play"></i> Run Scan';
      btn.disabled = false;
      alert('Scan complete! 3 new anomalies detected.');
    }, 2000);
  }
});

// Refresh button
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn');
  if (btn?.textContent.includes('Refresh')) {
    const icon = btn.querySelector('i');
    icon.classList.add('fa-spin');
    
    setTimeout(() => {
      icon.classList.remove('fa-spin');
      populateTables();
      refreshCharts();
    }, 1000);
  }
});

// ═════════════════════════════════════════════════════════════════
// EXPOSE FUNCTIONS
// ═════════════════════════════════════════════════════════════════
window.viewUserDetail = viewUserDetail;
