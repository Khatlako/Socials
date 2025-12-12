// Main JavaScript utilities

// Toast notifications
function showToast(message, type = 'info') {
    const alertClass = `alert-${type}`;
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    const container = document.querySelector('.main-content') || document.body;
    container.insertAdjacentHTML('afterbegin', alertHTML);
}

// AJAX requests with CSRF protection
function fetchData(url, options = {}) {
    const headers = options.headers || {};
    if (options.method && options.method !== 'GET') {
        headers['X-Requested-With'] = 'XMLHttpRequest';
    }
    
    return fetch(url, {
        ...options,
        headers
    });
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Format time
function formatTime(date) {
    return new Date(date).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Auto-save functionality
function setupAutoSave(formSelector, saveUrl) {
    const form = document.querySelector(formSelector);
    if (!form) return;
    
    const autoSave = debounce(() => {
        const formData = new FormData(form);
        fetch(saveUrl, {
            method: 'POST',
            body: formData
        })
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                showToast('Auto-saved', 'success');
            }
        })
        .catch(e => console.error('Auto-save failed:', e));
    }, 1000);
    
    form.addEventListener('change', autoSave);
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', () => {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(el => new bootstrap.Tooltip(el));
});

// Character counter for textareas
document.addEventListener('DOMContentLoaded', () => {
    const textareas = document.querySelectorAll('textarea[data-char-limit]');
    textareas.forEach(textarea => {
        const limit = textarea.getAttribute('data-char-limit');
        const counter = document.createElement('small');
        counter.className = 'text-muted d-block mt-1';
        counter.textContent = `0 / ${limit}`;
        textarea.parentElement.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            counter.textContent = `${this.value.length} / ${limit}`;
            if (this.value.length >= limit) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        });
    });
});

console.log('Main JS loaded');
