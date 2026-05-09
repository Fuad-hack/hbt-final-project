/**
 * SentinelAI Login Page JavaScript
 * Authentication and UI interactions
 */

// API Configuration
const API_BASE_URL = window.location.origin;

// DOM Elements
const loginForm = document.getElementById('loginForm');
const loginBtn = document.getElementById('loginBtn');
const btnText = loginBtn.querySelector('.btn-text');
const btnLoader = loginBtn.querySelector('.btn-loader');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('password');
const demoCards = document.querySelectorAll('.demo-card');
const activityFeed = document.getElementById('activityFeed');

// Security Events for Activity Feed
const securityEvents = [
  { icon: 'fa-user-shield', text: 'Anomaly detected: User USR-4821', type: 'warning' },
  { icon: 'fa-file-export', text: 'Bulk download: 247 files accessed', type: 'alert' },
  { icon: 'fa-usb', text: 'USB device connected: USR-3156', type: 'info' },
  { icon: 'fa-envelope', text: 'External email: sensitive keywords', type: 'warning' },
  { icon: 'fa-lock', text: 'Failed login: USR-7823 (3 attempts)', type: 'alert' },
  { icon: 'fa-clock', text: 'After-hours access: USR-1234', type: 'info' },
  { icon: 'fa-database', text: 'DB query anomaly detected', type: 'warning' },
  { icon: 'fa-network-wired', text: 'VPN origin anomaly: USR-5567', type: 'alert' }
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initializeActivityFeed();
  animateStats();
  
  // Check if already logged in
  const token = localStorage.getItem('access_token');
  if (token) {
    // Verify token is still valid
    verifyToken(token).then(valid => {
      if (valid) {
        window.location.href = '/dashboard';
      } else {
        localStorage.removeItem('access_token');
      }
    });
  }
});

// Toggle Password Visibility
togglePassword.addEventListener('click', () => {
  const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
  passwordInput.setAttribute('type', type);
  togglePassword.innerHTML = type === 'password' 
    ? '<i class="fas fa-eye"></i>' 
    : '<i class="fas fa-eye-slash"></i>';
});

// Demo Card Click
demoCards.forEach(card => {
  card.addEventListener('click', () => {
    const username = card.dataset.user;
    const password = card.dataset.pass;
    
    document.getElementById('username').value = username;
    document.getElementById('password').value = password;
    
    // Visual feedback
    card.style.transform = 'scale(0.95)';
    setTimeout(() => {
      card.style.transform = '';
    }, 150);
  });
});

// Login Form Submit
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const rememberMe = document.getElementById('rememberMe').checked;
  
  if (!username || !password) {
    showError('Please enter both username and password');
    return;
  }
  
  // Show loading state
  setLoading(true);
  hideError();
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Store token
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      if (rememberMe) {
        localStorage.setItem('remember_user', username);
      }
      
      // Success animation
      loginBtn.classList.add('success-animation');
      btnText.innerHTML = '<i class="fas fa-check"></i> Access Granted';
      
      // Redirect after animation
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 800);
    } else {
      showError(data.error || 'Invalid credentials');
      setLoading(false);
      
      // Shake animation on error
      loginCardShake();
    }
  } catch (error) {
    showError('Connection error. Please try again.');
    setLoading(false);
    console.error('Login error:', error);
  }
});

// Helper Functions
function setLoading(loading) {
  if (loading) {
    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    loginBtn.disabled = true;
  } else {
    btnText.style.display = 'flex';
    btnLoader.style.display = 'none';
    loginBtn.disabled = false;
  }
}

function showError(message) {
  errorText.textContent = message;
  errorMessage.style.display = 'flex';
}

function hideError() {
  errorMessage.style.display = 'none';
}

function loginCardShake() {
  const card = document.querySelector('.login-card');
  card.style.animation = 'shake 0.5s ease';
  setTimeout(() => {
    card.style.animation = '';
  }, 500);
}

async function verifyToken(token) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.ok;
  } catch {
    return false;
  }
}

// Activity Feed
function initializeActivityFeed() {
  // Add initial items
  for (let i = 0; i < 4; i++) {
    addActivityItem();
  }
  
  // Add new item every 3-6 seconds
  setInterval(() => {
    if (Math.random() > 0.3) {
      addActivityItem();
    }
  }, 4000);
}

function addActivityItem() {
  const event = securityEvents[Math.floor(Math.random() * securityEvents.length)];
  const item = document.createElement('div');
  item.className = 'feed-item';
  item.innerHTML = `
    <i class="fas ${event.icon}"></i>
    <div class="feed-content">
      <span class="feed-text">${event.text}</span>
      <span class="feed-time">${getTimeAgo()}</span>
    </div>
  `;
  
  activityFeed.insertBefore(item, activityFeed.firstChild);
  
  // Keep only 5 items
  while (activityFeed.children.length > 5) {
    activityFeed.removeChild(activityFeed.lastChild);
  }
  
  // Fade in animation
  item.style.opacity = '0';
  item.style.transform = 'translateY(-10px)';
  setTimeout(() => {
    item.style.transition = 'all 0.3s ease';
    item.style.opacity = '1';
    item.style.transform = 'translateY(0)';
  }, 10);
}

function getTimeAgo() {
  const seconds = Math.floor(Math.random() * 60) + 1;
  return seconds < 10 ? 'Just now' : `${seconds}s ago`;
}

// Animated Stats
function animateStats() {
  const stats = ['usersMonitored', 'threatsDetected', 'modelsActive'];
  
  stats.forEach((statId, index) => {
    const element = document.getElementById(statId);
    if (element) {
      setTimeout(() => {
        element.style.transform = 'scale(1.1)';
        element.style.color = '#00d4ff';
        setTimeout(() => {
          element.style.transform = 'scale(1)';
          element.style.color = '';
        }, 300);
      }, index * 800 + 1000);
    }
  });
}

// Add shake animation to CSS dynamically
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
  }
`;
document.head.appendChild(shakeStyle);
