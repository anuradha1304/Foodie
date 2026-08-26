
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
