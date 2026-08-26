import os
from functools import partial
open = partial(open, encoding="utf-8")

static_dir = "d:/Downloads/files/src/main/resources/static"
admin_dir = os.path.join(static_dir, "admin")
js_admin_dir = os.path.join(static_dir, "js", "admin")

os.makedirs(admin_dir, exist_ok=True)
os.makedirs(js_admin_dir, exist_ok=True)

# 1. admin/dashboard.html
with open(os.path.join(admin_dir, "dashboard.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard - FoodApp</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
    <style>
        .tabs { display: flex; border-bottom: 2px solid var(--border-color); margin-bottom: 2rem; gap: 1rem; overflow-x: auto; }
        .tab { padding: 0.75rem 1.5rem; cursor: pointer; border-bottom: 3px solid transparent; color: var(--text-muted); font-weight: 500; white-space: nowrap; }
        .tab:hover { color: var(--text-main); }
        .tab.active { color: var(--accent); border-bottom-color: var(--accent); }
        .order-card { background: white; border-radius: var(--radius); padding: 1.5rem; box-shadow: var(--shadow-sm); margin-bottom: 1rem; display: flex; flex-direction: column; gap: 1rem; }
        @media (min-width: 768px) { .order-card { flex-direction: row; justify-content: space-between; align-items: center; } }
        .switch { position: relative; display: inline-block; width: 40px; height: 20px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--text-muted); transition: .4s; border-radius: 20px; }
        .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 2px; bottom: 2px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: var(--success); }
        input:checked + .slider:before { transform: translateX(20px); }
    </style>
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp Admin</a>
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
                    <span style="font-size: 0.875rem; font-weight: 500;">Restaurant Open</span>
                    <label class="switch">
                        <input type="checkbox" id="toggle-restaurant-status">
                        <span class="slider"></span>
                    </label>
                </label>
                <nav id="nav-links" class="nav-links"></nav>
            </div>
        </div>
    </header>
    <main class="container mt-4">
        <h1>Order Queue</h1>
        <div class="tabs" id="status-tabs">
            <div class="tab active" data-status="PLACED">New Orders</div>
            <div class="tab" data-status="ACCEPTED">Accepted</div>
            <div class="tab" data-status="PREPARING">Preparing</div>
            <div class="tab" data-status="OUT_FOR_DELIVERY">Out for Delivery</div>
            <div class="tab" data-status="COMPLETED">Completed</div>
        </div>
        
        <div id="queue-container">
            <p>Loading...</p>
        </div>
        
        <!-- Reject Modal -->
        <div id="reject-modal" class="d-none" style="position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:1000; display:flex; align-items:center; justify-content:center;">
            <div style="background:white; padding:2rem; border-radius:var(--radius); width:100%; max-width:400px; box-shadow:var(--shadow-lg);">
                <h3>Reject Order</h3>
                <p class="text-muted" style="margin-bottom:1rem; font-size:0.875rem;">Please provide a reason for rejecting this order.</p>
                <textarea id="reject-reason" class="form-control" rows="3" placeholder="E.g., Item out of stock"></textarea>
                <div style="display:flex; justify-content:flex-end; gap:1rem; margin-top:1.5rem;">
                    <button id="btn-close-reject" class="btn btn-outline">Cancel</button>
                    <button id="btn-confirm-reject" class="btn btn-primary" style="background:var(--accent);">Reject</button>
                </div>
            </div>
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
    <script type="module" src="/js/admin/dashboard.js"></script>
</body>
</html>
""")

# 2. js/admin/dashboard.js
with open(os.path.join(js_admin_dir, "dashboard.js"), "w") as f:
    f.write("""
import { api } from '../api.js';
import { formatMoney, showToast } from '../ui.js';
import { checkSession } from '../auth.js';

let currentTab = 'PLACED';
let pollInterval;
let activeOrderIdForReject = null;

async function loadQueue() {
    const container = document.getElementById('queue-container');
    try {
        let statusFilter = currentTab;
        if (currentTab === 'COMPLETED') statusFilter = '';
        const data = await api.get(`/api/admin/orders?status=${statusFilter}&page=0&size=50`);
        
        let orders = data.content;
        if (currentTab === 'COMPLETED') {
            orders = orders.filter(o => o.status === 'DELIVERED' || o.status === 'REJECTED' || o.status === 'CANCELLED');
        }
        
        if (orders.length === 0) {
            container.innerHTML = `<p class="text-muted text-center" style="padding:2rem;">No orders in this status.</p>`;
            return;
        }
        
        container.innerHTML = '';
        orders.forEach(o => {
            const placedAt = new Date(o.placedAt);
            const elapsed = Math.floor((new Date() - placedAt) / 60000);
            
            const card = document.createElement('div');
            card.className = 'order-card';
            
            let actionHtml = '';
            if (o.status === 'PLACED') {
                actionHtml = `
                    <button class="btn btn-primary btn-accept" data-id="${o.id}">Accept Order</button>
                    <button class="btn btn-outline btn-reject" data-id="${o.id}" style="color:var(--accent); border-color:var(--accent);">Reject</button>
                `;
            } else if (o.status === 'ACCEPTED') {
                actionHtml = `<button class="btn btn-primary btn-advance" data-id="${o.id}" data-next="PREPARING">Start Preparing</button>`;
            } else if (o.status === 'PREPARING') {
                actionHtml = `<button class="btn btn-primary btn-advance" data-id="${o.id}" data-next="OUT_FOR_DELIVERY">Send out for Delivery</button>`;
            } else if (o.status === 'OUT_FOR_DELIVERY') {
                actionHtml = `<button class="btn btn-primary btn-advance" data-id="${o.id}" data-next="DELIVERED">Mark Delivered</button>`;
            }
            
            card.innerHTML = `
                <div>
                    <h3 style="margin-bottom:0.25rem;">${o.orderNumber}</h3>
                    <p style="font-weight:600; color:var(--text-main); margin-bottom:0.5rem;">${o.customerName} • ${o.customerPhone}</p>
                    <div style="font-size:0.875rem; color:var(--text-muted); display:flex; gap:1rem;">
                        <span>${o.itemCount} items</span>
                        <span>${formatMoney(o.totalAmount)}</span>
                        <span>Placed ${elapsed} min ago</span>
                    </div>
                </div>
                <div style="display:flex; gap:1rem; flex-wrap:wrap; align-items:center;">
                    ${actionHtml || `<span style="font-weight:600; padding:0.5rem; background:var(--bg-color); border-radius:4px;">${o.status.replace(/_/g, ' ')}</span>`}
                </div>
            `;
            container.appendChild(card);
        });
        
        attachEventListeners();
        
    } catch(e) {
        container.innerHTML = '<p class="text-muted text-center">Failed to load queue.</p>';
    }
}

function attachEventListeners() {
    document.querySelectorAll('.btn-accept').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            e.target.disabled = true;
            try {
                await api.post(`/api/admin/orders/${id}/accept`);
                showToast('Order Accepted', 'success');
                loadQueue();
            } catch(err) { handleConflict(err); }
        });
    });
    
    document.querySelectorAll('.btn-reject').forEach(btn => {
        btn.addEventListener('click', (e) => {
            activeOrderIdForReject = e.target.getAttribute('data-id');
            document.getElementById('reject-modal').classList.remove('d-none');
        });
    });
    
    document.querySelectorAll('.btn-advance').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            const nextStatus = e.target.getAttribute('data-next');
            e.target.disabled = true;
            try {
                await api.patch(`/api/admin/orders/${id}/status`, { status: nextStatus, note: 'Updated by admin' });
                showToast(`Order marked as ${nextStatus.replace(/_/g, ' ')}`, 'success');
                loadQueue();
            } catch(err) { handleConflict(err); }
        });
    });
}

function handleConflict(err) {
    if (err.status === 409) {
        showToast('This order was just updated elsewhere. Refreshing...', 'error');
        loadQueue();
    } else {
        showToast(err.message || 'Action failed', 'error');
    }
}

// Reject Modal logic
document.getElementById('btn-close-reject').addEventListener('click', () => {
    document.getElementById('reject-modal').classList.add('d-none');
    document.getElementById('reject-reason').value = '';
    activeOrderIdForReject = null;
});

document.getElementById('btn-confirm-reject').addEventListener('click', async () => {
    const reason = document.getElementById('reject-reason').value;
    if (!reason) { showToast('Reason is required', 'error'); return; }
    
    try {
        await api.post(`/api/admin/orders/${activeOrderIdForReject}/reject`, { reason });
        showToast('Order Rejected', 'success');
        document.getElementById('reject-modal').classList.add('d-none');
        loadQueue();
    } catch(err) { handleConflict(err); }
});

// Tabs logic
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        currentTab = e.target.getAttribute('data-status');
        loadQueue();
        
        clearInterval(pollInterval);
        if (currentTab === 'PLACED') {
            pollInterval = setInterval(loadQueue, 15000); // 15s auto-refresh for New Orders
        }
    });
});

// Init
checkSession().then(user => {
    if (user && user.role === 'RESTAURANT_ADMIN') {
        loadQueue();
        pollInterval = setInterval(loadQueue, 15000);
        
        // Load restaurant status (a bit hacky since we just have one endpoint that requires boolean)
        // In a real app we'd fetch the restaurant details. Assuming it is Open by default.
        const toggle = document.getElementById('toggle-restaurant-status');
        toggle.checked = true; 
        toggle.addEventListener('change', async (e) => {
            try {
                await api.patch('/api/admin/restaurant/status', { isOpen: e.target.checked });
                showToast(e.target.checked ? 'Restaurant is now OPEN' : 'Restaurant is now CLOSED', 'success');
            } catch(err) {
                e.target.checked = !e.target.checked; // revert
                showToast(err.message, 'error');
            }
        });
    }
});
""")

# 3. admin/menu.html
with open(os.path.join(admin_dir, "menu.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Menu Management - FoodApp Admin</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
    <style>
        .menu-table { width: 100%; border-collapse: collapse; background: white; border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow-sm); }
        .menu-table th, .menu-table td { padding: 1rem; text-align: left; border-bottom: 1px solid var(--border-color); }
        .menu-table th { background: var(--bg-color); font-weight: 600; color: var(--text-muted); font-size: 0.875rem; text-transform: uppercase; }
        .menu-table tr:last-child td { border-bottom: none; }
        .switch { position: relative; display: inline-block; width: 40px; height: 20px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--text-muted); transition: .4s; border-radius: 20px; }
        .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 2px; bottom: 2px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: var(--success); }
        input:checked + .slider:before { transform: translateX(20px); }
    </style>
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp Admin</a>
            <nav id="nav-links" class="nav-links"></nav>
        </div>
    </header>
    <main class="container mt-4">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2rem;">
            <h1>Menu Management</h1>
            <button id="btn-new-item" class="btn btn-primary">+ Add Item</button>
        </div>
        
        <div style="overflow-x:auto;">
            <table class="menu-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Available</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="menu-tbody">
                    <tr><td colspan="5" class="text-center text-muted">Loading...</td></tr>
                </tbody>
            </table>
        </div>
        
        <!-- Menu Item Modal -->
        <div id="item-modal" class="d-none" style="position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:1000; display:flex; align-items:center; justify-content:center; padding:1rem;">
            <div style="background:white; padding:2rem; border-radius:var(--radius); width:100%; max-width:500px; box-shadow:var(--shadow-lg); max-height:90vh; overflow-y:auto;">
                <h3 id="modal-title">Add Menu Item</h3>
                <form id="item-form" class="mt-4">
                    <input type="hidden" id="item-id">
                    <div class="form-group">
                        <label class="form-label" for="itemName">Name</label>
                        <input type="text" id="itemName" name="name" class="form-control" required>
                        <span class="form-error" id="error-name"></span>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="itemCategory">Category</label>
                        <input type="text" id="itemCategory" name="category" class="form-control" required>
                        <span class="form-error" id="error-category"></span>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="itemDescription">Description</label>
                        <textarea id="itemDescription" name="description" class="form-control" rows="2"></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="itemPrice">Price</label>
                        <input type="number" step="0.01" id="itemPrice" name="price" class="form-control" required>
                        <span class="form-error" id="error-price"></span>
                    </div>
                    <div style="display:flex; justify-content:flex-end; gap:1rem; margin-top:2rem;">
                        <button type="button" id="btn-close-modal" class="btn btn-outline">Cancel</button>
                        <button type="submit" class="btn btn-primary" id="btn-save-item">Save Item</button>
                    </div>
                </form>
            </div>
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
    <script type="module" src="/js/admin/menu-admin.js"></script>
</body>
</html>
""")

# 4. js/admin/menu-admin.js
with open(os.path.join(js_admin_dir, "menu-admin.js"), "w") as f:
    f.write("""
import { api } from '../api.js';
import { formatMoney, showToast, clearFormErrors, showFormErrors } from '../ui.js';

let menuItems = [];

async function loadMenu() {
    const tbody = document.getElementById('menu-tbody');
    try {
        menuItems = await api.get('/api/admin/menu');
        
        if (menuItems.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No menu items found.</td></tr>';
            return;
        }
        
        // Filter out logically deleted items just in case the backend returns them
        menuItems = menuItems.filter(m => !m.isDeleted);
        
        tbody.innerHTML = '';
        menuItems.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <div style="font-weight:600;">${item.name}</div>
                    <div style="font-size:0.75rem; color:var(--text-muted);">${item.description || ''}</div>
                </td>
                <td><span style="background:var(--bg-color); padding:0.25rem 0.5rem; border-radius:4px; font-size:0.75rem;">${item.category}</span></td>
                <td style="font-weight:600;">${formatMoney(item.price)}</td>
                <td>
                    <label class="switch">
                        <input type="checkbox" class="toggle-availability" data-id="${item.id}" ${item.available ? 'checked' : ''}>
                        <span class="slider"></span>
                    </label>
                </td>
                <td>
                    <div style="display:flex; gap:0.5rem;">
                        <button class="btn btn-outline btn-edit" data-id="${item.id}" style="padding:0.25rem 0.5rem; font-size:0.75rem;">Edit</button>
                        <button class="btn btn-outline btn-delete" data-id="${item.id}" style="padding:0.25rem 0.5rem; font-size:0.75rem; color:var(--accent); border-color:transparent;">Delete</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
        
        attachEventListeners();
        
    } catch(e) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Error loading menu.</td></tr>';
    }
}

function attachEventListeners() {
    document.querySelectorAll('.toggle-availability').forEach(toggle => {
        toggle.addEventListener('change', async (e) => {
            const id = e.target.getAttribute('data-id');
            const isAvailable = e.target.checked;
            try {
                await api.patch(`/api/admin/menu/${id}/availability`, { isAvailable });
                showToast(`Item marked ${isAvailable ? 'available' : 'unavailable'}`, 'success');
            } catch(err) {
                e.target.checked = !isAvailable; // rollback optimistic UI
                showToast(err.message, 'error');
            }
        });
    });
    
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.getAttribute('data-id'));
            const item = menuItems.find(m => m.id === id);
            openModal(item);
        });
    });
    
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this item?')) {
                try {
                    await api.del(`/api/admin/menu/${id}`);
                    showToast('Item deleted', 'success');
                    loadMenu();
                } catch(err) { showToast(err.message, 'error'); }
            }
        });
    });
}

// Modal Logic
const modal = document.getElementById('item-modal');
const form = document.getElementById('item-form');

document.getElementById('btn-new-item').addEventListener('click', () => openModal());
document.getElementById('btn-close-modal').addEventListener('click', () => {
    modal.classList.add('d-none');
    form.reset();
    clearFormErrors(form);
});

function openModal(item = null) {
    clearFormErrors(form);
    if (item) {
        document.getElementById('modal-title').textContent = 'Edit Menu Item';
        document.getElementById('item-id').value = item.id;
        form.itemName.value = item.name;
        form.itemCategory.value = item.category;
        form.itemDescription.value = item.description || '';
        form.itemPrice.value = item.price;
    } else {
        document.getElementById('modal-title').textContent = 'Add Menu Item';
        document.getElementById('item-id').value = '';
        form.reset();
    }
    modal.classList.remove('d-none');
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearFormErrors(form);
    const btn = document.getElementById('btn-save-item');
    btn.disabled = true;
    
    const id = document.getElementById('item-id').value;
    const payload = {
        name: form.itemName.value,
        category: form.itemCategory.value,
        description: form.itemDescription.value,
        price: parseFloat(form.itemPrice.value),
        isAvailable: true // Default to true when creating/editing here
    };
    
    try {
        if (id) {
            await api.put(`/api/admin/menu/${id}`, payload);
            showToast('Item updated successfully', 'success');
        } else {
            await api.post('/api/admin/menu', payload);
            showToast('Item created successfully', 'success');
        }
        modal.classList.add('d-none');
        loadMenu();
    } catch(err) {
        if (err.status === 400 && err.fieldErrors) {
            showFormErrors(form, err.fieldErrors);
        } else {
            showToast(err.message, 'error');
        }
    } finally {
        btn.disabled = false;
    }
});

loadMenu();
""")
