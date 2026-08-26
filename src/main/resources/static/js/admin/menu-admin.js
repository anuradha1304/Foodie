
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
