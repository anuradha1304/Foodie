import os
from functools import partial
open = partial(open, encoding="utf-8")

static_dir = "d:/Downloads/files/src/main/resources/static"
js_dir = os.path.join(static_dir, "js")

# 1. Update index.html for Restaurant Search
with open(os.path.join(static_dir, "index.html"), "r") as f:
    index_content = f.read()

new_index_main = """    <main class="container mt-4">
        <h1 class="text-center">Welcome to FoodApp</h1>
        <p class="text-center text-muted">Browse restaurants and order your favorite food!</p>
        
        <div class="search-bar" style="display: flex; gap: 1rem; margin-top: 2rem; align-items: center;">
            <input type="text" id="search-input" class="form-control" placeholder="Search restaurants..." style="flex: 1;">
            <select id="cuisine-select" class="form-control" style="width: 200px;">
                <option value="">All Cuisines</option>
            </select>
            <label style="display: flex; align-items: center; gap: 0.5rem; white-space: nowrap;">
                <input type="checkbox" id="open-only-checkbox"> Open Only
            </label>
        </div>
        
        <div id="restaurant-grid" class="mt-4" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem;">
            <!-- Rendered by restaurants.js -->
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
    <script type="module" src="/js/restaurants.js"></script>
</body>"""
index_content = index_content.replace("""    <main class="container mt-4">
        <h1 class="text-center">Welcome to FoodApp</h1>
        <p class="text-center text-muted">Browse restaurants and order your favorite food!</p>
        <div id="restaurant-grid" class="mt-4">
            <!-- Rendered by restaurants.js (M8b) -->
            <p class="text-center text-muted">Restaurants will appear here...</p>
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
</body>""", new_index_main)

with open(os.path.join(static_dir, "index.html"), "w") as f:
    f.write(index_content)

# 2. restaurants.js
with open(os.path.join(js_dir, "restaurants.js"), "w") as f:
    f.write("""
import { api } from './api.js';

let debounceTimeout;

async function loadCuisines() {
    const cuisines = await api.get('/api/restaurants/cuisines');
    const select = document.getElementById('cuisine-select');
    if(cuisines) {
        cuisines.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            select.appendChild(opt);
        });
    }
}

async function loadRestaurants() {
    const search = document.getElementById('search-input').value;
    const cuisine = document.getElementById('cuisine-select').value;
    const openOnly = document.getElementById('open-only-checkbox').checked;
    
    let url = `/api/restaurants?openOnly=${openOnly}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (cuisine) url += `&cuisine=${encodeURIComponent(cuisine)}`;
    
    const grid = document.getElementById('restaurant-grid');
    grid.innerHTML = '<p class="text-muted">Loading...</p>';
    
    const page = await api.get(url);
    if (!page || page.content.length === 0) {
        grid.innerHTML = '<p class="text-muted" style="grid-column: 1/-1; text-align: center;">No restaurants found.</p>';
        return;
    }
    
    grid.innerHTML = '';
    page.content.forEach(r => {
        const card = document.createElement('a');
        card.href = `/menu.html?restaurantId=${r.id}`;
        card.className = 'restaurant-card';
        card.style.display = 'block';
        card.style.background = 'var(--bg-surface)';
        card.style.borderRadius = 'var(--radius)';
        card.style.padding = '1rem';
        card.style.boxShadow = 'var(--shadow-sm)';
        card.style.textDecoration = 'none';
        card.style.color = 'inherit';
        
        card.innerHTML = `
            <h3 style="margin-bottom: 0.5rem; color: var(--accent);">${r.name}</h3>
            <p style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 1rem;">${r.cuisineType} • ${r.address}</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; background: ${r.isOpen ? 'var(--success)' : 'var(--text-muted)'}; color: white; border-radius: 4px;">
                    ${r.isOpen ? 'OPEN' : 'CLOSED'}
                </span>
            </div>
        `;
        grid.appendChild(card);
    });
}

function handleSearch() {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(loadRestaurants, 300);
}

document.getElementById('search-input').addEventListener('input', handleSearch);
document.getElementById('cuisine-select').addEventListener('change', loadRestaurants);
document.getElementById('open-only-checkbox').addEventListener('change', loadRestaurants);

loadCuisines();
loadRestaurants();
""")

# 3. menu.html & menu.js
with open(os.path.join(static_dir, "menu.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Menu - FoodApp</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
    <style>
        .menu-category { margin-top: 2rem; margin-bottom: 1rem; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; }
        .menu-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
        .menu-item-card { background: white; padding: 1rem; border-radius: var(--radius); box-shadow: var(--shadow-sm); display: flex; flex-direction: column; justify-content: space-between; }
        .unavailable { opacity: 0.6; pointer-events: none; }
    </style>
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp</a>
            <nav id="nav-links" class="nav-links"></nav>
        </div>
    </header>
    <main class="container mt-4">
        <div id="restaurant-info"></div>
        <div id="menu-container"></div>
    </main>
    <script type="module" src="/js/auth.js"></script>
    <script type="module" src="/js/menu.js"></script>
</body>
</html>
""")

with open(os.path.join(js_dir, "menu.js"), "w") as f:
    f.write("""
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
""")

# 4. cart.html & cart.js
with open(os.path.join(static_dir, "cart.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cart - FoodApp</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp</a>
            <nav id="nav-links" class="nav-links"></nav>
        </div>
    </header>
    <main class="container mt-4" style="max-width: 800px;">
        <h1>Your Cart</h1>
        <div id="cart-container" class="mt-4">
            <p>Loading cart...</p>
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
    <script type="module" src="/js/cart.js"></script>
</body>
</html>
""")

with open(os.path.join(js_dir, "cart.js"), "w") as f:
    f.write("""
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
""")

# 5. checkout.html & checkout.js
with open(os.path.join(static_dir, "checkout.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Checkout - FoodApp</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp</a>
            <nav id="nav-links" class="nav-links"></nav>
        </div>
    </header>
    <main class="container mt-4" style="max-width: 600px;">
        <h1>Checkout</h1>
        <div id="checkout-container" class="mt-4" style="background: var(--bg-surface); border-radius: var(--radius); padding: 1.5rem; box-shadow: var(--shadow-sm);">
            <div id="checkout-summary" style="margin-bottom: 2rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
                <p>Loading summary...</p>
            </div>
            <form id="checkout-form">
                <div class="form-group">
                    <label class="form-label" for="deliveryAddress">Delivery Address</label>
                    <textarea id="deliveryAddress" name="deliveryAddress" class="form-control" rows="3" required></textarea>
                    <span class="form-error" id="error-deliveryAddress"></span>
                </div>
                <div class="form-group">
                    <label class="form-label" for="customerNote">Note to Restaurant (Optional)</label>
                    <input type="text" id="customerNote" name="customerNote" class="form-control">
                </div>
                <button type="submit" id="btn-place-order" class="btn btn-primary" style="width: 100%;">Place Order</button>
            </form>
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
    <script type="module" src="/js/checkout.js"></script>
</body>
</html>
""")

with open(os.path.join(js_dir, "checkout.js"), "w") as f:
    f.write("""
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
""")

# 6. order-confirmation.html
with open(os.path.join(static_dir, "order-confirmation.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Order Confirmed - FoodApp</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp</a>
            <nav id="nav-links" class="nav-links"></nav>
        </div>
    </header>
    <main class="container mt-4 auth-wrapper">
        <div class="auth-card text-center" style="max-width:500px;">
            <div style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;">✅</div>
            <h1 style="margin-bottom: 1rem;">Order Placed!</h1>
            <p class="text-muted" style="margin-bottom: 2rem;">Your order <strong id="order-num" style="color:var(--text-main);"></strong> has been successfully placed.</p>
            <div style="display:flex; gap:1rem; justify-content:center;">
                <a href="/index.html" class="btn btn-outline">Home</a>
                <button id="btn-track" class="btn btn-primary">Track Order</button>
            </div>
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
    <script>
        const params = new URLSearchParams(window.location.search);
        const onum = params.get('orderNumber');
        document.getElementById('order-num').textContent = onum;
        document.getElementById('btn-track').addEventListener('click', () => {
            // Need order ID, but we only have orderNumber in URL. 
            // We should either redirect to order history or tracking page by querying list
            window.location.href = '/order-history.html';
        });
    </script>
</body>
</html>
""")

# 7. order-history.html & history.js
with open(os.path.join(static_dir, "order-history.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Order History - FoodApp</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp</a>
            <nav id="nav-links" class="nav-links"></nav>
        </div>
    </header>
    <main class="container mt-4" style="max-width:800px;">
        <h1>Your Orders</h1>
        <div id="history-container" class="mt-4">
            <p>Loading...</p>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:2rem;">
            <button id="btn-prev" class="btn btn-outline d-none">Previous</button>
            <button id="btn-next" class="btn btn-outline d-none">Next</button>
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
    <script type="module" src="/js/history.js"></script>
</body>
</html>
""")

with open(os.path.join(js_dir, "history.js"), "w") as f:
    f.write("""
import { api } from './api.js';
import { formatMoney } from './ui.js';

let currentPage = 0;

function getStatusColor(status) {
    if (status === 'DELIVERED') return 'var(--success)';
    if (status === 'CANCELLED' || status === 'REJECTED') return 'var(--accent)';
    return 'var(--warning)';
}

async function loadHistory(page) {
    const container = document.getElementById('history-container');
    try {
        const data = await api.get(`/api/orders?page=${page}&size=10`);
        if (!data || data.content.length === 0) {
            container.innerHTML = '<p class="text-muted text-center" style="padding:2rem;">You have no past orders.</p>';
            return;
        }
        
        container.innerHTML = '';
        data.content.forEach(o => {
            const date = new Date(o.placedAt).toLocaleString();
            const card = document.createElement('a');
            card.href = `/order-tracking.html?orderId=${o.id}`;
            card.style.display = 'block';
            card.style.background = 'var(--bg-surface)';
            card.style.borderRadius = 'var(--radius)';
            card.style.padding = '1rem 1.5rem';
            card.style.marginBottom = '1rem';
            card.style.boxShadow = 'var(--shadow-sm)';
            card.style.textDecoration = 'none';
            card.style.color = 'inherit';
            
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <div>
                        <h4 style="margin:0;">${o.restaurantName}</h4>
                        <span class="text-muted" style="font-size:0.875rem;">${date} • ${o.orderNumber}</span>
                    </div>
                    <div style="text-align:right;">
                        <span style="display:inline-block; padding:0.25rem 0.5rem; background:${getStatusColor(o.status)}; color:white; border-radius:4px; font-size:0.75rem; font-weight:600;">
                            ${o.status.replace(/_/g, ' ')}
                        </span>
                        <div style="font-weight:600; margin-top:0.25rem; color:var(--accent);">${formatMoney(o.totalAmount)}</div>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
        
        const btnPrev = document.getElementById('btn-prev');
        const btnNext = document.getElementById('btn-next');
        
        if (!data.first) {
            btnPrev.classList.remove('d-none');
            btnPrev.onclick = () => loadHistory(page - 1);
        } else { btnPrev.classList.add('d-none'); }
        
        if (!data.last) {
            btnNext.classList.remove('d-none');
            btnNext.onclick = () => loadHistory(page + 1);
        } else { btnNext.classList.add('d-none'); }
        
        currentPage = page;
        
    } catch(e) {
        container.innerHTML = '<p class="text-muted">Error loading history.</p>';
    }
}

loadHistory(0);
""")

# 8. order-tracking.html & tracking.js
with open(os.path.join(static_dir, "order-tracking.html"), "w") as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Track Order - FoodApp</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="/css/base.css">
    <link rel="stylesheet" href="/css/components.css">
    <style>
        .stepper { display: flex; justify-content: space-between; position: relative; margin: 3rem 0; }
        .stepper::before { content: ''; position: absolute; top: 50%; left: 0; right: 0; height: 4px; background: var(--border-color); transform: translateY(-50%); z-index: 1; }
        .stepper-progress { position: absolute; top: 50%; left: 0; height: 4px; background: var(--success); transform: translateY(-50%); z-index: 1; transition: width 0.3s; }
        .step { position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center; width: 60px; }
        .step-circle { width: 30px; height: 30px; border-radius: 50%; background: var(--bg-surface); border: 4px solid var(--border-color); transition: all 0.3s; }
        .step.active .step-circle { border-color: var(--success); background: var(--success); }
        .step-label { margin-top: 0.5rem; font-size: 0.75rem; font-weight: 600; color: var(--text-muted); text-align: center; white-space: nowrap; }
        .step.active .step-label { color: var(--text-main); }
    </style>
</head>
<body>
    <header class="header">
        <div class="container header-inner">
            <a href="/index.html" class="logo">FoodApp</a>
            <nav id="nav-links" class="nav-links"></nav>
        </div>
    </header>
    <main class="container mt-4" style="max-width: 800px;">
        <div style="background: var(--bg-surface); border-radius: var(--radius); padding: 2rem; box-shadow: var(--shadow-sm);">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-color); padding-bottom:1rem; margin-bottom:1rem;">
                <div>
                    <h2 id="track-order-number">Loading...</h2>
                    <p id="track-restaurant-name" class="text-muted"></p>
                </div>
                <div style="text-align:right;">
                    <span id="track-status-badge" style="display:inline-block; padding:0.5rem 1rem; background:var(--bg-color); color:var(--text-main); border-radius:var(--radius-sm); font-weight:700;"></span>
                </div>
            </div>
            
            <div class="stepper" id="stepper">
                <div class="stepper-progress" id="stepper-progress" style="width:0%;"></div>
                <div class="step" data-step="0"><div class="step-circle"></div><div class="step-label">Placed</div></div>
                <div class="step" data-step="1"><div class="step-circle"></div><div class="step-label">Accepted</div></div>
                <div class="step" data-step="2"><div class="step-circle"></div><div class="step-label">Preparing</div></div>
                <div class="step" data-step="3"><div class="step-circle"></div><div class="step-label">Out for Delivery</div></div>
                <div class="step" data-step="4"><div class="step-circle"></div><div class="step-label">Delivered</div></div>
            </div>
            
            <div id="rejection-box" class="d-none" style="background:var(--accent-light); color:var(--accent); padding:1rem; border-radius:var(--radius-sm); margin-bottom:1.5rem;">
                <strong>Order Rejected:</strong> <span id="rejection-reason"></span>
            </div>
            
            <div id="cancel-box" class="d-none" style="text-align:center; margin-top:2rem;">
                <button id="btn-cancel" class="btn btn-outline" style="color:var(--accent); border-color:var(--accent);">Cancel Order</button>
            </div>
        </div>
    </main>
    <script type="module" src="/js/auth.js"></script>
    <script type="module" src="/js/tracking.js"></script>
</body>
</html>
""")

with open(os.path.join(js_dir, "tracking.js"), "w") as f:
    f.write("""
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
""")
