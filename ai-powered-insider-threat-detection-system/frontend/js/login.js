/**
 * Sentinel ITP Admin Console JavaScript
 * Authentication and UI interactions
 */

// API Configuration - Backend runs on port 5000
const API_BASE_URL = 'http://localhost:5000';

// DEBUG: Log connection info
console.log('API_BASE_URL:', API_BASE_URL);
console.log('Current location:', window.location.href);

// Check if opened directly (file://)
if (window.location.protocol === 'file:') {
  alert('⚠️ ERROR: Do not open this file directly!\n\nUse: http://localhost:3000/login\n\nBackend: http://localhost:5000\nServer must be running.');
}

// DOM Elements - with null checks
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const errorText = document.getElementById('errorText');
const successText = document.getElementById('successText');
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('login-password');
const btnText = loginBtn?.querySelector('.btn-text');
const demoChips = document.querySelectorAll('.btn-quick');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  // Check if already logged in
  const token = localStorage.getItem('access_token');
  if (token) {
    verifyToken(token).then(valid => {
      if (valid) {
        window.location.href = '/enterprise';
      } else {
        localStorage.removeItem('access_token');
      }
    });
  }
  
  initThemeToggle();
});

// Theme Toggle
function initThemeToggle() {
  const themeToggle = document.querySelector('.theme-toggle');
  const icon = themeToggle?.querySelector('i');
  
  // Load saved theme
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
    if (icon) {
      icon.classList.remove('fa-sun');
      icon.classList.add('fa-moon');
    }
  }
  
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-theme');
      const isLight = document.body.classList.contains('light-theme');
      
      // Update icon
      if (icon) {
        if (isLight) {
          icon.classList.remove('fa-sun');
          icon.classList.add('fa-moon');
        } else {
          icon.classList.remove('fa-moon');
          icon.classList.add('fa-sun');
        }
      }
      
      // Save preference
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });
  }
}

function hideMessages() {
  errorMessage.style.display = 'none';
  successMessage.style.display = 'none';
}

// Toggle Password Visibility
togglePassword.addEventListener('click', () => {
  const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
  passwordInput.setAttribute('type', type);
  togglePassword.innerHTML = type === 'password' 
    ? '<i class="fas fa-eye"></i>' 
    : '<i class="fas fa-eye-slash"></i>';
});

// Register password toggles
const toggleRegPassword = document.getElementById('toggleRegPassword');
const toggleRegConfirm = document.getElementById('toggleRegConfirm');
const regPasswordInput = document.getElementById('reg-password');
const regConfirmInput = document.getElementById('reg-confirm');

if (toggleRegPassword && regPasswordInput) {
  toggleRegPassword.addEventListener('click', () => {
    const type = regPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    regPasswordInput.setAttribute('type', type);
    toggleRegPassword.innerHTML = type === 'password' 
      ? '<i class="fas fa-eye"></i>' 
      : '<i class="fas fa-eye-slash"></i>';
  });
}

if (toggleRegConfirm && regConfirmInput) {
  toggleRegConfirm.addEventListener('click', () => {
    const type = regConfirmInput.getAttribute('type') === 'password' ? 'text' : 'password';
    regConfirmInput.setAttribute('type', type);
    toggleRegConfirm.innerHTML = type === 'password' 
      ? '<i class="fas fa-eye"></i>' 
      : '<i class="fas fa-eye-slash"></i>';
  });
}

// Quick Access Button Click
demoChips.forEach(chip => {
  chip.addEventListener('click', () => {
    const username = chip.dataset.user;
    const password = chip.dataset.pass;
    document.getElementById('login-username').value = username;
    document.getElementById('login-password').value = password;
    hideError();
    // Auto submit
    loginForm.dispatchEvent(new Event('submit'));
    // Visual feedback
    chip.style.transform = 'scale(0.95)';
    setTimeout(() => {
      chip.style.transform = '';
    }, 150);
  });
});

// Login Form Submit
console.log('🔍 DEBUG: loginForm found:', !!loginForm);

if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    console.log('🔔 DEBUG: Login form submitted!');
    e.preventDefault();
    
    const username = document.getElementById('login-username')?.value.trim();
    const password = document.getElementById('login-password')?.value;
    const rememberMe = document.getElementById('rememberMe')?.checked;
    
    console.log('🔔 DEBUG: username:', username);
    console.log('🔔 DEBUG: API_BASE_URL:', API_BASE_URL);
  
  if (!username || !password) {
    showError('Please enter both username and password');
    return;
  }
  
  // Show loading state
  setLoading(true);
  hideError();
  
  try {
    console.log('📤 Sending login request to:', `${API_BASE_URL}/api/auth/login`);
    console.log('📤 Request body:', JSON.stringify({ username, password: '***' }));
    
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    });
    
    console.log('📥 Response status:', response.status);
    console.log('📥 Response ok:', response.ok);
    
    const data = await response.json();
    console.log('📥 Response data:', data);
    
    if (response.ok) {
      // Store token
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      if (rememberMe) {
        localStorage.setItem('remember_user', username);
      }
      
      // Success animation
      loginBtn.classList.add('success-animation');
      if (btnText) {
        btnText.innerHTML = '<i class="fas fa-check"></i> Access Granted';
      }
      
      // Redirect after animation
      setTimeout(() => {
        window.location.href = '/enterprise';
      }, 800);
    } else {
      showError(data.error || 'Invalid credentials');
      setLoading(false);
      
      // Error animation
      loginBtn.classList.add('shake');
      setTimeout(() => loginBtn.classList.remove('shake'), 500);
    }
  } catch (error) {
    console.error('Login error details:', error);
    console.error('Error name:', error.name);
    console.error('Error message:', error.message);
    console.error('API_BASE_URL used:', API_BASE_URL);
    
    if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
      showError('Cannot connect to server.\n\n1. Check if server is running: python run.py\n2. Use: http://localhost:5000/login\n3. Do not open file directly!');
    } else {
      showError('Connection error: ' + error.message);
    }
    setLoading(false);
  }
  });
}

// Register Form Submit
if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const name = document.getElementById('reg-name').value.trim();
  const company = document.getElementById('reg-company').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const confirm = document.getElementById('reg-confirm').value;
  const agreeTerms = document.getElementById('agreeTerms').checked;
  
  // Use name as username if not provided separately
  const username = name.toLowerCase().replace(/\s+/g, '_');
  
  if (!name || !email || !password || !confirm) {
    showError('Please fill in all required fields');
    return;
  }
  
  if (!agreeTerms) {
    showError('Please agree to the Terms and Privacy Policy');
    return;
  }
  
  if (password !== confirm) {
    showError('Passwords do not match');
    return;
  }
  
  if (password.length < 6) {
    showError('Password must be at least 6 characters');
    return;
  }
  
  // Show loading state
  setButtonLoading(registerBtn, true);
  hideMessages();
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        name,
        email, 
        password
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showSuccess('Account created successfully! Please login.');
      setTimeout(() => {
        // Switch to login view
        registerBox.style.display = 'none';
        loginBox.style.display = 'block';
        // Pre-fill username
        document.getElementById('login-username').value = username;
      }, 1500);
    } else {
      showError(data.error || 'Registration failed');
    }
  } catch (error) {
    console.error('Register error details:', error);
    console.error('Error name:', error.name);
    console.error('Error message:', error.message);
    if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
      showError('Cannot connect to server.\n\n1. Check if server is running: python run.py\n2. Use: http://localhost:5000/login');
    } else {
      showError('Connection error: ' + error.message);
    }
  } finally {
    setButtonLoading(registerBtn, false);
  }
  });
}

// Password Strength Indicator
const regPassword = document.getElementById('reg-password');
const passwordMeter = document.getElementById('passwordMeter');

if (regPassword && passwordMeter) {
  regPassword.addEventListener('input', (e) => {
    const value = e.target.value;
    let strength = 0;
    
    if (value.length >= 6) strength++;
    if (value.length >= 10) strength++;
    if (/[a-z]/.test(value) && /[A-Z]/.test(value)) strength++;
    if (/[0-9]/.test(value)) strength++;
    if (/[^a-zA-Z0-9]/.test(value)) strength++;
    
    passwordMeter.className = 'password-meter';
    if (value.length > 0) {
      if (strength <= 2) {
        passwordMeter.classList.add('weak');
      } else if (strength <= 4) {
        passwordMeter.classList.add('medium');
      } else {
        passwordMeter.classList.add('strong');
      }
    }
  });
}

// Sign In / Sign Up Toggle - Get elements safely
const showRegister = document.getElementById('showRegister');
const showLogin = document.getElementById('showLogin');
const loginBox = document.querySelector('.login-box');
const registerBox = document.getElementById('registerBox');

if (showRegister && loginBox && registerBox) {
  showRegister.addEventListener('click', (e) => {
    e.preventDefault();
    loginBox.style.display = 'none';
    registerBox.style.display = 'block';
    hideError();
    hideSuccess();
  });
}

if (showLogin && loginBox && registerBox) {
  showLogin.addEventListener('click', (e) => {
    e.preventDefault();
    registerBox.style.display = 'none';
    loginBox.style.display = 'block';
    hideError();
    hideSuccess();
  });
}

// Helper Functions
function setLoading(loading) {
  if (loading) {
    loginBtn.classList.add('loading');
    loginBtn.disabled = true;
  } else {
    loginBtn.classList.remove('loading');
    loginBtn.disabled = false;
  }
}

function setButtonLoading(btn, loading) {
  if (loading) {
    btn.classList.add('loading');
    btn.disabled = true;
  } else {
    btn.classList.remove('loading');
    btn.disabled = false;
  }
}

function showError(message) {
  errorText.textContent = message;
  errorMessage.style.display = 'flex';
  successMessage.style.display = 'none';
}

function showSuccess(message) {
  successText.textContent = message;
  successMessage.style.display = 'flex';
  errorMessage.style.display = 'none';
}

function hideError() {
  errorMessage.style.display = 'none';
}

function hideSuccess() {
  successMessage.style.display = 'none';
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

