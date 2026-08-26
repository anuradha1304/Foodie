
export function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        container.setAttribute('aria-live', 'polite');
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, type === 'success' ? 2500 : 4000);
}

export function formatMoney(value) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(value);
}

export function clearFormErrors(form) {
    form.querySelectorAll('.form-error').forEach(el => el.textContent = '');
    form.querySelectorAll('.form-control').forEach(el => el.style.borderColor = '');
}

export function showFormErrors(form, fieldErrors) {
    if (!fieldErrors) return;
    for (const [field, error] of Object.entries(fieldErrors)) {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            input.style.borderColor = 'var(--accent)';
            const errorEl = document.getElementById(`error-${field}`);
            if (errorEl) errorEl.textContent = error;
        }
    }
}
