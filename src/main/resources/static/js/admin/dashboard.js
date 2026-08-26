
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
