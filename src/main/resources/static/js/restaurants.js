
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
