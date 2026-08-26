
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
