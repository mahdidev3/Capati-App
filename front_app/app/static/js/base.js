// Global variables and functions used across the application

// Fix RTL icon margins
function fixRTLIconMargins() {
    // Run immediately
    applyIconMargins();

    // Run multiple times to catch delayed icon replacements
    const intervals = [50, 100, 200, 500, 1000, 1500, 2000, 3000];
    intervals.forEach(delay => {
        setTimeout(applyIconMargins, delay);
    });

    // Also watch for changes continuously
    const observer = new MutationObserver(function(mutations) {
        applyIconMargins();
    });

    // Observe the entire document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'data-feather']
    });

    // Re-apply on every animation frame for first 5 seconds
    let startTime = Date.now();
    function continuousApply() {
        applyIconMargins();
        if (Date.now() - startTime < 5000) {
            requestAnimationFrame(continuousApply);
        }
    }
    requestAnimationFrame(continuousApply);
}

function applyIconMargins() {
    // All sidebar navigation icons
    document.querySelectorAll('#sidebar .nav-link svg, .sidebar-nav .nav-link svg, .sidebar .nav-link svg').forEach(function(icon) {
        icon.style.setProperty('margin-right', '0', 'important');
        icon.style.setProperty('margin-left', '0.75rem', 'important');
        icon.style.setProperty('width', '20px', 'important');
        icon.style.setProperty('height', '20px', 'important');
    });

    // Sidebar brand icon
    document.querySelectorAll('.sidebar-brand svg').forEach(function(icon) {
        icon.style.setProperty('margin-right', '0', 'important');
        icon.style.setProperty('margin-left', '0.75rem', 'important');
    });

    // User avatar and logout button - no margins
    document.querySelectorAll('.user-avatar svg, .logout-btn svg').forEach(function(icon) {
        icon.style.setProperty('margin', '0', 'important');
    });
}

// Show message to user
function showMessage(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Find the page header and insert alert after it
    const pageHeader = document.querySelector('.page-header');
    if (pageHeader) {
        pageHeader.insertAdjacentElement('afterend', alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Fix RTL icon margins
    fixRTLIconMargins();
    
    // Initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Auto-dismiss alerts after 5 seconds
    document.addEventListener('DOMContentLoaded', function() {
        const autoDismissAlerts = document.querySelectorAll('.auto-dismiss');
        autoDismissAlerts.forEach(function(alert) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    });
});