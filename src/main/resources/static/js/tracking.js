
import { api } from './api.js';
import { showToast } from './ui.js';

const params = new URLSearchParams(window.location.search);
const orderId = params.get('orderId');
let pollInterval;

const stages = ['PLACED', 'ACCEPTED', 'PREPARING', 'OUT_FOR_DELIVERY', 'DELIVERED'];

async function loadFullOrder() {
    try {
        const order = await api.get(`/api/orders/${orderId}`);
        document.getElementById('track-order-number').textContent = order.orderNumber;
        document.getElementById('track-restaurant-name').textContent = order.restaurantName;
        updateUI(order);
    } catch(e) { showToast('Failed to load order', 'error'); }
}

async function pollStatus() {
    if (document.hidden) return; // Don't poll if tab is hidden
    try {
        const statusData = await api.get(`/api/orders/${orderId}/status`);
        updateUI(statusData);
    } catch(e) {}
}

function updateUI(data) {
    const status = data.status;
    const badge = document.getElementById('track-status-badge');
    badge.textContent = status.replace(/_/g, ' ');
    
    // Stop polling if terminal
    if (status === 'DELIVERED' || status === 'REJECTED' || status === 'CANCELLED') {
        clearInterval(pollInterval);
    }
    
    if (status === 'REJECTED') {
        badge.style.background = 'var(--accent)';
        badge.style.color = 'white';
        const hist = data.statusHistory.find(h => h.status === 'REJECTED');
        if (hist && hist.note) {
            document.getElementById('rejection-box').classList.remove('d-none');
            document.getElementById('rejection-reason').textContent = hist.note;
        }
        document.getElementById('stepper').style.display = 'none';
        return;
    }
    if (status === 'CANCELLED') {
        badge.style.background = 'var(--text-muted)';
        badge.style.color = 'white';
        document.getElementById('stepper').style.display = 'none';
        return;
    }
    
    // Stepper logic
    let stageIndex = stages.indexOf(status);
    if (stageIndex >= 0) {
        document.querySelectorAll('.step').forEach((el, idx) => {
            if (idx <= stageIndex) el.classList.add('active');
            else el.classList.remove('active');
        });
        document.getElementById('stepper-progress').style.width = `${(stageIndex / (stages.length - 1)) * 100}%`;
    }
    
    // Cancel button logic
    const cancelBox = document.getElementById('cancel-box');
    if (status === 'PLACED') {
        cancelBox.classList.remove('d-none');
    } else {
        cancelBox.classList.add('d-none');
    }
}

document.getElementById('btn-cancel').addEventListener('click', async () => {
    const reason = prompt('Reason for cancellation?');
    if (reason) {
        try {
            await api.post(`/api/orders/${orderId}/cancel`, { reason });
            showToast('Order cancelled', 'success');
            loadFullOrder();
        } catch(e) { showToast(e.message, 'error'); }
    }
});

document.addEventListener('visibilitychange', () => {
    if (!document.hidden) pollStatus();
});

window.addEventListener('beforeunload', () => clearInterval(pollInterval));

if (orderId) {
    loadFullOrder();
    pollInterval = setInterval(pollStatus, 5000);
}
