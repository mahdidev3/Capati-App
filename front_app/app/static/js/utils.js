// Utility functions used across the application

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format duration
function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    if (minutes >= 60) {
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return `${hours}:${remainingMinutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.flash-messages') || document.body;
    container.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('متن با موفقیت کپی شد', 'success');
    }, function(err) {
        console.error('Could not copy text: ', err);
        showNotification('خطا در کپی متن', 'error');
    });
}

// Validate phone number
function validatePhoneNumber(phone) {
    const phoneRegex = /^09[0-9]{9}$/;
    return phoneRegex.test(phone);
}

// Validate email
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Get operation cost based on type and resolution
function getOperationCost(operationType, resolution = '720p') {
    // Get base cost based on operation type (for 720p or lower) - in credits
    const baseCosts = {
        'english_subtitle': 3,  // 3 credits = 3000 tomans
        'persian_subtitle': 4,  // 4 credits = 4000 tomans
        'persian_dubbing': 5,   // 5 credits = 5000 tomans
        'persian_dubbing_english_subtitle': 6, // 6 credits = 6000 tomans
        'persian_dubbing_persian_subtitle': 6  // 6 credits = 6000 tomans
    };

    let baseCost = baseCosts[operationType] || 3;

    // Adjust cost based on resolution
    let height = 720; // Default
    if (resolution && typeof resolution === 'string') {
        if (resolution.includes('x')) {
            height = parseInt(resolution.split('x')[1]);
        } else if (resolution.toLowerCase().includes('p')) {
            height = parseInt(resolution.toLowerCase().replace('p', ''));
        }
    } else if (typeof resolution === 'number') {
        height = resolution;
    }

    // Apply multiplier based on quality
    let multiplier = 1.0;
    if (height > 1080) {
        multiplier = 2.0;  // 4K: 2x base cost
    } else if (height > 720) {
        multiplier = 1.5;  // Full HD: 1.5x base cost
    }
    // 720p and below: base cost (multiplier = 1.0)

    return Math.ceil(baseCost * multiplier * 1000); // Convert to Tomans
}

// Get operation name in Persian
function getOperationName(operationType) {
    const names = {
        'english_subtitle': 'زیرنویس انگلیسی',
        'persian_subtitle': 'زیرنویس فارسی',
        'persian_dubbing': 'دوبله فارسی',
        'persian_dubbing_english_subtitle': 'دوبله فارسی و زیرنویس انگلیسی',
        'persian_dubbing_persian_subtitle': 'دوبله فارسی و زیرنویس فارسی'
    };
    return names[operationType] || operationType;
}