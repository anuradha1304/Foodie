
import { api } from './api.js';
import { formatMoney, showToast } from './ui.js';

const params = new URLSearchParams(window.location.search);
const restaurantId = params.get('restaurantId');

async function loadMenu() {
    if (!restaurantId) return;
    
    try {
        const [restaurant, menu] = await Promise.all([
            api.get(`/api/restaurants/${restaurantId}`),
            api.get(`/api/restaurants/${restaurantId}/menu`)
        ]);
        
        document.getElementById('restaurant-info').innerHTML = `
            <h1>${restaurant.name}</h1>
            <p class="text-muted">${restaurant.cuisineType} • ${restaurant.address}</p>
        `;
        
        const container = document.getElementById('menu-container');
        if (!menu || menu.categories.length === 0) {
            container.innerHTML = '<p>No menu items available.</p>';
            return;
        }
        
        menu.categories.forEach(cat => {
            const h2 = document.createElement('h2');
            h2.className = 'menu-category';
            h2.textContent = cat.categoryName;
            container.appendChild(h2);
            
            const grid = document.createElement('div');
            grid.className = 'menu-grid';
            
            cat.items.forEach(item => {
                const card = document.createElement('div');
                card.className = `menu-item-card ${!item.isAvailable ? 'unavailable' : ''}`;
                card.innerHTML = `
                    <div>
                        <h4 style="margin-bottom:0.25rem;">${item.name}</h4>
                        <p class="text-muted" style="font-size:0.875rem;">${item.description || ''}</p>
                        <p style="font-weight:600; margin-top:0.5rem; color:var(--accent);">${formatMoney(item.price)}</p>
                    </div>
                    <div style="margin-top:1rem;">
                        ${!item.isAvailable ? '<span style="color:var(--warning); font-size:0.875rem;">Currently unavailable</span>' : `
                            <div style="display:flex; gap:0.5rem; align-items:center;">
                                <input type="number" id="qty-${item.id}" value="1" min="1" max="20" class="form-control" style="width:70px; padding:0.25rem;">
                                <button class="btn btn-outline btn-add" data-id="${item.id}" data-rid="${restaurant.id}">Add to Cart</button>
                            </div>
                        `}
                    </div>
                `;
                grid.appendChild(card);
            });
            container.appendChild(grid);
        });
        
        document.querySelectorAll('.btn-add').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const menuItemId = e.target.getAttribute('data-id');
                const rid = e.target.getAttribute('data-rid');
                const qty = document.getElementById(`qty-${menuItemId}`).value;
                e.target.disabled = true;
                e.target.textContent = 'Adding...';
                
                try {
                    const cart = await api.post('/api/cart/items', { menuItemId: parseInt(menuItemId), quantity: parseInt(qty) });
                    showToast('Added to cart', 'success');
                    updateCartBadge(cart.itemCount);
                } catch(err) {
                    if (err.code === 'CART_RESTAURANT_MISMATCH') {
                        if (confirm(`Your cart has items from another restaurant. Clear it and add this instead?`)) {
                            await api.del('/api/cart');
                            const cart = await api.post('/api/cart/items', { menuItemId: parseInt(menuItemId), quantity: parseInt(qty) });
                            showToast('Cart cleared and item added', 'success');
                            updateCartBadge(cart.itemCount);
                        }
                    } else if (err.code === 'UNAUTHENTICATED') {
                        window.location.href = '/login.html';
                    } else {
                        showToast(err.message, 'error');
                    }
                } finally {
                    e.target.disabled = false;
                    e.target.textContent = 'Add to Cart';
                }
            });
        });
        
    } catch(e) {
        document.getElementById('menu-container').innerHTML = '<p class="text-muted">Failed to load menu.</p>';
    }
}

function updateCartBadge(count) {
    const badge = document.getElementById('nav-cart-badge');
    if (badge) badge.textContent = count;
}

loadMenu();
