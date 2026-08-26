
import { api } from './api.js';
import { formatMoney, showToast } from './ui.js';

async function loadCart() {
    try {
        const cart = await api.get('/api/cart');
        renderCart(cart);
    } catch(e) {
        document.getElementById('cart-container').innerHTML = '<p>Error loading cart.</p>';
    }
}

function renderCart(cart) {
    const container = document.getElementById('cart-container');
    const badge = document.getElementById('nav-cart-badge');
    if (badge) badge.textContent = cart.itemCount;

    if (!cart.items || cart.items.length === 0) {
        container.innerHTML = `
            <div class="text-center" style="padding: 3rem; background: var(--bg-surface); border-radius: var(--radius);">
                <h3 class="text-muted">Your cart is empty</h3>
                <a href="/index.html" class="btn btn-primary mt-4">Browse Restaurants</a>
            </div>
        `;
        return;
    }
    
    let html = `
        <div style="background: var(--bg-surface); border-radius: var(--radius); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <h3 style="margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">
                Order from ${cart.restaurantName}
            </h3>
    `;
    
    cart.items.forEach(item => {
        html += `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid var(--border-color);">
                <div style="flex: 1;">
                    <h4 style="margin:0;">${item.name}</h4>
                    <div style="color: var(--text-muted); font-size: 0.875rem;">${formatMoney(item.unitPrice)} each</div>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <button class="btn btn-outline btn-update-qty" data-id="${item.cartItemId}" data-qty="${item.quantity - 1}">-</button>
                        <span style="min-width:20px; text-align:center;">${item.quantity}</span>
                        <button class="btn btn-outline btn-update-qty" data-id="${item.cartItemId}" data-qty="${item.quantity + 1}">+</button>
                    </div>
                    <div style="font-weight: 600; min-width:80px; text-align:right;">${formatMoney(item.lineTotal)}</div>
                    <button class="btn btn-outline btn-remove" data-id="${item.cartItemId}" style="padding: 0.25rem 0.5rem; color:var(--accent); border-color:transparent;">✕</button>
                </div>
            </div>
        `;
    });
    
    html += `
            <div style="margin-top: 1.5rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span class="text-muted">Subtotal</span>
                    <span>${formatMoney(cart.subtotal)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color);">
                    <span class="text-muted">Delivery Fee</span>
                    <span>${formatMoney(cart.deliveryFee)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 1.25rem; margin-bottom: 1.5rem;">
                    <span>Total</span>
                    <span style="color:var(--accent);">${formatMoney(cart.total)}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <button id="btn-clear" class="btn btn-outline" style="color:var(--text-muted); border-color:var(--border-color);">Clear Cart</button>
                    <a href="/checkout.html" class="btn btn-primary">Proceed to Checkout</a>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    document.querySelectorAll('.btn-update-qty').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            const qty = parseInt(e.target.getAttribute('data-qty'));
            try {
                const updatedCart = await api.put(`/api/cart/items/${id}`, { quantity: qty });
                renderCart(updatedCart);
            } catch(err) {
                showToast(err.message, 'error');
            }
        });
    });
    
    document.querySelectorAll('.btn-remove').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const id = e.target.getAttribute('data-id');
            try {
                const updatedCart = await api.del(`/api/cart/items/${id}`);
                renderCart(updatedCart);
            } catch(err) { showToast(err.message, 'error'); }
        });
    });
    
    document.getElementById('btn-clear')?.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear your cart?')) {
            try {
                const updatedCart = await api.del('/api/cart');
                renderCart(updatedCart);
            } catch(err) { showToast(err.message, 'error'); }
        }
    });
}

loadCart();
