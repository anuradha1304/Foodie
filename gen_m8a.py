import os

static_dir = "d:/Downloads/files/src/main/resources/static"
css_dir = os.path.join(static_dir, "css")
js_dir = os.path.join(static_dir, "js")

os.makedirs(css_dir, exist_ok=True)
os.makedirs(js_dir, exist_ok=True)

# 1. CSS files
with open(os.path.join(css_dir, "base.css"), "w") as f:
    f.write("""
:root {
  --accent: #E23744;
  --accent-hover: #C52935;
  --accent-light: #FDE8EA;
  --bg-color: #F8F9FA;
  --bg-surface: #FFFFFF;
  --text-main: #2D3748;
  --text-muted: #718096;
  --border-color: #E2E8F0;
  --success: #38A169;
  --warning: #DD6B20;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
  --radius: 12px;
  --radius-sm: 8px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font-sans);
  background-color: var(--bg-color);
  color: var(--text-main);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

a { color: var(--accent); text-decoration: none; transition: color 0.2s; }
a:hover { color: var(--accent-hover); }

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  font-family: var(--font-sans);
}
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary {
  background: linear-gradient(135deg, var(--accent), #ff5a66);
  color: white;
  box-shadow: 0 4px 10px rgba(226, 55, 68, 0.3);
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(226, 55, 68, 0.4);
}
.btn-primary:active:not(:disabled) { transform: translateY(0); }
.btn-outline {
  background: transparent;
  color: var(--accent);
  border: 1px solid var(--accent);
}
.btn-outline:hover:not(:disabled) { background: var(--accent-light); }

/* Forms */
.form-group { margin-bottom: 1rem; }
.form-label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.25rem; }
.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-control:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}
.form-error { color: var(--accent); font-size: 0.75rem; margin-top: 0.25rem; display: block; }

/* Layout */
.container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
.header {
  background: var(--bg-surface);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}
.logo { font-size: 1.5rem; font-weight: 700; color: var(--accent); letter-spacing: -0.5px; }
.nav-links { display: flex; gap: 1.5rem; align-items: center; }

/* Utilities */
.text-center { text-align: center; }
.mt-4 { margin-top: 1rem; }
.mb-4 { margin-bottom: 1rem; }
.d-none { display: none !important; }
""")

with open(os.path.join(css_dir, "components.css"), "w") as f:
    f.write("""
/* Toast */
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.toast {
  background: white;
  padding: 1rem;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-lg);
  min-width: 300px;
  transform: translateX(120%);
  animation: slideIn 0.3s forwards cubic-bezier(0.16, 1, 0.3, 1);
  border-left: 4px solid var(--text-muted);
}
.toast.success { border-left-color: var(--success); }
.toast.error { border-left-color: var(--accent); }
@keyframes slideIn { to { transform: translateX(0); } }
@keyframes fadeOut { to { opacity: 0; } }

/* Spinner */
.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Auth Container */
.auth-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 70px);
  padding: 2rem 1rem;
}
.auth-card {
  background: var(--bg-surface);
  padding: 2.5rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  width: 100%;
  max-width: 400px;
}
.auth-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; text-align: center; }
""")

# 2. JS files
with open(os.path.join(js_dir, "api.js"), "w") as f:
    f.write("""
const BASE = '';

function csrfToken() {
  return document.cookie.split('; ')
    .find(c => c.startsWith('XSRF-TOKEN='))?.split('=')[1];
}

class ApiError extends Error {
  constructor(code, message, fieldErrors, status) {
    super(message);
    this.code = code;
    this.fieldErrors = fieldErrors;
    this.status = status;
  }
}

async function request(method, path, body, extraHeaders = {}) {
  const headers = { 'Accept': 'application/json', ...extraHeaders };
  if (body) headers['Content-Type'] = 'application/json';
  if (method !== 'GET') {
    const token = csrfToken();
    if (token) headers['X-XSRF-TOKEN'] = decodeURIComponent(token);
  }

  const res = await fetch(BASE + path, {
    method, headers,
    credentials: 'same-origin',
    body: body ? JSON.stringify(body) : undefined
  });

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    if (res.status === 401 && path !== '/api/auth/me' && path !== '/api/auth/login') { 
        window.location.href = '/login.html'; 
        return; 
    }
    throw new ApiError(data?.code ?? 'INTERNAL_ERROR',
                       data?.message ?? 'Something went wrong',
                       data?.fieldErrors, res.status);
  }
  return data;
}

export const api = {
  get:  (p)       => request('GET', p),
  post: (p, b, h) => request('POST', p, b, h),
  put:  (p, b)    => request('PUT', p, b),
  patch:(p, b)    => request('PATCH', p, b),
  del:  (p)       => request('DELETE', p)
};
""")

with open(os.path.join(js_dir, "ui.js"), "w") as f:
    f.write("""
export function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        container.setAttribute('aria-live', 'polite');
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, type === 'success' ? 2500 : 4000);
}

export function formatMoney(value) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(value);
}

export function clearFormErrors(form) {
    form.querySelectorAll('.form-error').forEach(el => el.textContent = '');
    form.querySelectorAll('.form-control').forEach(el => el.style.borderColor = '');
}

export function showFormErrors(form, fieldErrors) {
    if (!fieldErrors) return;
    for (const [field, error] of Object.entries(fieldErrors)) {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            input.style.borderColor = 'var(--accent)';
            const errorEl = document.getElementById(`error-${field}`);
            if (errorEl) errorEl.textContent = error;
        }
    }
}
""")

with open(os.path.join(js_dir, "auth.js"), "w") as f:
    f.write("""
import { api } from './api.js';
import { showToast } from './ui.js';

let currentUser = null;

export async function checkSession() {
    try {
        currentUser = await api.get('/api/auth/me');
        updateNav();
        return currentUser;
    } catch (e) {
        currentUser = null;
        updateNav();
        return null;
    }
}

export function getUser() {
    return currentUser;
}

export async function logout() {
    try {
        await api.post('/api/auth/logout');
        window.location.href = '/index.html';
    } catch (e) {
        showToast('Logout failed', 'error');
    }
}

function updateNav() {
    const navLinks = document.getElementById('nav-links');
    if (!navLinks) return;
    
    if (currentUser) {
        if (currentUser.role === 'CUSTOMER') {
            navLinks.innerHTML = `
                <a href="/cart.html" class="nav-link">Cart <span id="nav-cart-badge" class="badge">0</span></a>
                <a href="/order-history.html" class="nav-link">Orders</a>
                <span class="user-greeting">Hi, ${currentUser.fullName}</span>
                <button id="btn-logout" class="btn btn-outline">Logout</button>
            `;
        } else if (currentUser.role === 'RESTAURANT_ADMIN') {
            navLinks.innerHTML = `
                <a href="/admin/dashboard.html" class="nav-link">Dashboard</a>
                <a href="/admin/menu.html" class="nav-link">Menu</a>
                <span class="user-greeting">Admin: ${currentUser.fullName}</span>
                <button id="btn-logout" class="btn btn-outline">Logout</button>
            `;
        }
        document.getElementById('btn-logout').addEventListener('click', logout);
    } else {
        navLinks.innerHTML = `
            <a href="/login.html" class="btn btn-outline">Log in</a>
            <a href="/register.html" class="btn btn-primary">Sign up</a>
        `;
    }
}

// Auto-check on load if not on login/register
if (!window.location.pathname.includes('login') && !window.location.pathname.includes('register')) {
    checkSession();
}
""")

# 3. HTML files
with open(os.path.join(static_dir, "index.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FoodApp - Order Food Online</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp</a>
            <nav id="nav-links" class="nav-links">
                <!-- Populated by auth.js -->
            </nav>
        </div>
    </header>
    <main class="container mt-4">
        <h1 class="text-center">Welcome to FoodApp</h1>
        <p class="text-center text-muted">Browse restaurants and order your favorite food!</p>
        <div id="restaurant-grid" class="mt-4">
            <!-- Rendered by restaurants.js (M8b) -->
            <p class="text-center text-muted">Restaurants will appear here...</p>
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
</body>
</html>
""")

with open(os.path.join(static_dir, "login.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - FoodApp</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp</a>
        </div>
    </header>
    <main class="auth-wrapper">
        <div class="auth-card">
            <h1 class="auth-title">Welcome Back</h1>
            <form id="login-form">
                <div class="form-group">
                    <label class="form-label" for="email">Email</label>
                    <input type="email" id="email" name="email" class="form-control" required>
                    <span class="form-error" id="error-email"></span>
                </div>
                <div class="form-group">
                    <label class="form-label" for="password">Password</label>
                    <input type="password" id="password" name="password" class="form-control" required>
                    <span class="form-error" id="error-password"></span>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%; margin-top:1rem;" id="btn-login">Log In</button>
            </form>
            <p class="text-center mt-4 text-muted" style="font-size:0.875rem">
                Don't have an account? <a href="/register.html">Sign up</a>
            </p>
        </div>
    </main>
    
    <script type="module">
        import { api } from '/js/api.js';
        import { checkSession } from '/js/auth.js';
        import { showToast, clearFormErrors, showFormErrors } from '/js/ui.js';

        // Check if already logged in
        checkSession().then(user => {
            if (user) {
                window.location.href = user.role === 'CUSTOMER' ? '/index.html' : '/admin/dashboard.html';
            }
        });

        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const btn = document.getElementById('btn-login');
            clearFormErrors(form);
            
            const email = form.email.value;
            const password = form.password.value;
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>';
            
            try {
                await api.post('/api/auth/login', { email, password });
                const user = await checkSession();
                if (user) {
                    window.location.href = user.role === 'CUSTOMER' ? '/index.html' : '/admin/dashboard.html';
                }
            } catch (err) {
                btn.disabled = false;
                btn.textContent = 'Log In';
                if (err.status === 400 && err.fieldErrors) {
                    showFormErrors(form, err.fieldErrors);
                } else {
                    showToast(err.message || 'Login failed', 'error');
                }
            }
        });
    </script>
</body>
</html>
""")

with open(os.path.join(static_dir, "register.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign Up - FoodApp</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp</a>
        </div>
    </header>
    <main class="auth-wrapper">
        <div class="auth-card">
            <h1 class="auth-title">Create Account</h1>
            <form id="register-form">
                <div class="form-group">
                    <label class="form-label" for="fullName">Full Name</label>
                    <input type="text" id="fullName" name="fullName" class="form-control" required>
                    <span class="form-error" id="error-fullName"></span>
                </div>
                <div class="form-group">
                    <label class="form-label" for="email">Email</label>
                    <input type="email" id="email" name="email" class="form-control" required>
                    <span class="form-error" id="error-email"></span>
                </div>
                <div class="form-group">
                    <label class="form-label" for="phone">Phone Number</label>
                    <input type="text" id="phone" name="phone" class="form-control" required>
                    <span class="form-error" id="error-phone"></span>
                </div>
                <div class="form-group">
                    <label class="form-label" for="password">Password</label>
                    <input type="password" id="password" name="password" class="form-control" required>
                    <span class="form-error" id="error-password"></span>
                </div>
                <div class="form-group">
                    <label class="form-label" for="role">I want to...</label>
                    <select id="role" name="role" class="form-control">
                        <option value="CUSTOMER">Order Food</option>
                        <option value="RESTAURANT_ADMIN">Manage a Restaurant</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%; margin-top:1rem;" id="btn-register">Sign Up</button>
            </form>
            <p class="text-center mt-4 text-muted" style="font-size:0.875rem">
                Already have an account? <a href="/login.html">Log in</a>
            </p>
        </div>
    </main>
    
    <script type="module">
        import { api } from '/js/api.js';
        import { checkSession } from '/js/auth.js';
        import { showToast, clearFormErrors, showFormErrors } from '/js/ui.js';

        // Check if already logged in
        checkSession().then(user => {
            if (user) {
                window.location.href = user.role === 'CUSTOMER' ? '/index.html' : '/admin/dashboard.html';
            }
        });

        document.getElementById('register-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const btn = document.getElementById('btn-register');
            clearFormErrors(form);
            
            const payload = {
                fullName: form.fullName.value,
                email: form.email.value,
                phone: form.phone.value,
                password: form.password.value,
                role: form.role.value
            };
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>';
            
            try {
                await api.post('/api/auth/register', payload);
                // On success, login automatically
                await api.post('/api/auth/login', { email: payload.email, password: payload.password });
                const user = await checkSession();
                if (user) {
                    window.location.href = user.role === 'CUSTOMER' ? '/index.html' : '/admin/dashboard.html';
                }
            } catch (err) {
                btn.disabled = false;
                btn.textContent = 'Sign Up';
                if (err.status === 400 && err.fieldErrors) {
                    showFormErrors(form, err.fieldErrors);
                } else {
                    showToast(err.message || 'Registration failed', 'error');
                }
            }
        });
    </script>
</body>
</html>
""")
