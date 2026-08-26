
import { api } from './api.js';
import { formatMoney, showToast, clearFormErrors, showFormErrors } from './ui.js';

let idempotencyKey = crypto.randomUUID();

async function loadCheckout() {
    try {
        const cart = await api.get('/api/cart');
        if (!cart.items || cart.items.length === 0) {
            window.location.href = '/cart.html';
            return;
        }
        
        const summary = document.getElementById('checkout-summary');
        summary.innerHTML = `
            <h3 style="margin-bottom:0.5rem;">Order from ${cart.restaurantName}</h3>
            <p style="color:var(--text-muted); margin-bottom:1rem;">${cart.itemCount} items</p>
            <div style="display:flex; justify-content:space-between; font-weight:700; font-size:1.25rem;">
                <span>Total to Pay:</span>
                <span style="color:var(--accent);">${formatMoney(cart.total)}</span>
            </div>
        `;
    } catch (e) {
        showToast('Error loading checkout', 'error');
    }
}

document.getElementById('checkout-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    clearFormErrors(form);
    const btn = document.getElementById('btn-place-order');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Placing...';
    
    const payload = {
        deliveryAddress: form.deliveryAddress.value,
        customerNote: form.customerNote.value
    };
    
    try {
        const order = await api.post('/api/orders', payload, { 'Idempotency-Key': idempotencyKey });
        window.location.href = `/order-confirmation.html?orderNumber=${order.orderNumber}`;
    } catch (err) {
        btn.disabled = false;
        btn.textContent = 'Place Order';
        
        if (err.status === 400 && err.fieldErrors) {
            showFormErrors(form, err.fieldErrors);
        } else if (err.status === 409) {
            showToast(err.message, 'error');
            setTimeout(() => window.location.href = '/cart.html', 3000);
        } else {
            showToast(err.message || 'Failed to place order', 'error');
        }
    }
});

loadCheckout();
