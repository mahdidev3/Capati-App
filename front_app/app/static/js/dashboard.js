// Dashboard specific JavaScript

// Global variables
let currentSection = 'dashboard';
let sidebarCollapsed = false;
let API_BASE_URL = '/api';

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    initializeFileUpload();
    initializeSidebar();
    initializeFormValidation();
    
    // Hide unsupported features
    hideUnsupportedFeatures();
});

// Hide unsupported features
function hideUnsupportedFeatures() {
    // Hide rating buttons
    const ratingButtons = document.querySelectorAll('[onclick*="showRatingModal"]');
    ratingButtons.forEach(button => {
        button.style.display = 'none';
        console.log('Rating feature is not supported by the backend API');
    });

    // Hide referral section
    const referralSection = document.querySelector('.card:has(h5:contains("برنامه معرفی"))');
    if (referralSection) {
        referralSection.style.display = 'none';
        console.log('Referral program is not supported by the backend API');
    }
}

// Dashboard initialization
function initializeDashboard() {
    // Set up navigation
    const navLinks = document.querySelectorAll('.nav-link[data-section]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            showSection(section);

            // Auto-close mobile menu after selection
            const sidebar = document.getElementById('sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            if (sidebar && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
                // Also remove overlay when closing menu
                if (overlay) {
                    overlay.classList.remove('show');
                }
            }
        });
    });

    // Initialize with dashboard section
    showSection('dashboard');
}

// Show specific section
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    // Show target section
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update navigation
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.classList.remove('active');
    });

    const activeNavLink = document.querySelector(`[data-section="${sectionName}"]`);
    if (activeNavLink) {
        const activeNavItem = activeNavLink.closest('.nav-item');
        if (activeNavItem) {
            activeNavItem.classList.add('active');
        }
    }

    currentSection = sectionName;

    // Initialize section-specific functionality
    if (sectionName === 'translate') {
        initializeTranslationForm();
    }
}

// Update user profile
function updateProfile() {
    const firstName = document.getElementById('first_name').value;
    const lastName = document.getElementById('last_name').value;

    fetch(`${API_BASE_URL}/account/profile`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
            firstName: firstName,
            lastName: lastName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('اطلاعات پروفایل با موفقیت به‌روزرسانی شد', 'success');
        } else {
            showMessage(data.message || 'خطا در به‌روزرسانی پروفایل', 'danger');
        }
    })
    .catch(error => {
        showMessage('خطا در ارسال درخواست', 'danger');
    });
}

// Change password
function changePassword() {
    const currentPassword = document.getElementById('current_password').value;
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    // Validate inputs
    if (!currentPassword || !newPassword || !confirmPassword) {
        showMessage('لطفا همه فیلدها را پر کنید', 'warning');
        return;
    }

    if (newPassword.length < 8) {
        showMessage('رمز عبور جدید باید حداقل 8 کاراکتر باشد', 'warning');
        return;
    }

    if (newPassword !== confirmPassword) {
        showMessage('رمز عبور جدید و تاییدیه یکسان نیستند', 'warning');
        return;
    }

    fetch(`${API_BASE_URL}/account/password`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
            currentPassword: currentPassword,
            newPassword: newPassword
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('رمز عبور با موفقیت تغییر یافت', 'success');
            // Clear form fields
            document.getElementById('current_password').value = '';
            document.getElementById('new_password').value = '';
            document.getElementById('confirm_password').value = '';
        } else {
            showMessage(data.message || 'خطا در تغییر رمز عبور', 'danger');
        }
    })
    .catch(error => {
        showMessage('خطا در ارسال درخواست', 'danger');
    });
}

// Sidebar functionality
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            toggleSidebar();
        });
    }

    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            toggleSidebar();
        });
    }

    // Handle responsive behavior
    function handleResize() {
        if (window.innerWidth <= 1240) {
            // Mobile behavior: sidebar starts hidden for screens smaller than 1240px
            if (sidebar) {
                sidebar.classList.remove('collapsed');
                sidebar.classList.remove('show');
            }
            if (mainContent) mainContent.classList.remove('expanded');
            sidebarCollapsed = false;
        } else {
            // Desktop behavior: sidebar always visible, can collapse to icons
            if (sidebar) {
                sidebar.classList.remove('show');
                if (sidebarCollapsed) {
                    sidebar.classList.add('collapsed');
                } else {
                    sidebar.classList.remove('collapsed');
                }
            }
            if (mainContent) mainContent.classList.toggle('expanded', sidebarCollapsed);
        }
    }

    window.addEventListener('resize', handleResize);
    handleResize();
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');

    if (!sidebar || !mainContent) return;

    if (window.innerWidth <= 1240) {
        // Mobile behavior: slide in/out for screens smaller than 1240px
        const isVisible = sidebar.classList.contains('show');
        sidebar.classList.toggle('show', !isVisible);

        // Toggle overlay
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            overlay.addEventListener('click', function() {
                sidebar.classList.remove('show');
                overlay.classList.remove('show');
            });
            document.body.appendChild(overlay);
        }
        overlay.classList.toggle('show', !isVisible);
    } else {
        // Desktop behavior: collapse to icons
        sidebarCollapsed = !sidebarCollapsed;
        sidebar.classList.toggle('collapsed', sidebarCollapsed);
        mainContent.classList.toggle('expanded', sidebarCollapsed);
    }
}

// File upload functionality
function initializeFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('video_file');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');

    if (!uploadArea || !fileInput) return;

    // Click to select file
    uploadArea.addEventListener('click', function(e) {
        if (e.target === uploadArea || uploadArea.contains(e.target)) {
            fileInput.click();
        }
    });

    // Drag and drop handlers
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect(files[0]);
        }
    });

    // File input change handler
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        // Validate file type - check both MIME type and extension
        const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/wmv', 'video/webm', 'video/x-msvideo', 'video/quicktime'];
        const allowedExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm', '.flv'];

        const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
        const isValidType = allowedTypes.includes(file.type) || allowedExtensions.includes(fileExtension);

        if (!isValidType) {
            alert('لطفاً یک فایل ویدیو معتبر انتخاب کنید (MP4, AVI, MOV, MKV, WMV, FLV, WEBM)');
            fileInput.value = ''; // Clear the input
            return;
        }

        // Display file info
        if (fileName && fileSize && fileInfo) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            fileInfo.style.display = 'block';

            // Show loading state
            const durationLoading = document.getElementById('durationLoading');
            if (durationLoading) {
                durationLoading.style.display = 'block';
            }
        }

        // Get actual video duration using HTML5 video element
        getActualVideoDuration(file).then(duration => {
            // Store duration for form submission
            window.selectedVideoDuration = duration;
            // Update hidden form input
            const durationInput = document.getElementById('durationInput');
            if (durationInput) {
                durationInput.value = duration;
            }

            // Try to detect video resolution from metadata
            detectVideoResolution(file).then(resolution => {
                window.selectedVideoResolution = resolution;
                const resolutionInput = document.getElementById('resolutionInput');
                if (resolutionInput) {
                    resolutionInput.value = window.selectedVideoResolution;
                }
                // Update cost preview with current form state
                recalculateCostAndDuration();
                updateOperationPrices(resolution);
            }).catch(() => {
                // Default resolution if detection fails
                window.selectedVideoResolution = '1280x720';
                const resolutionInput = document.getElementById('resolutionInput');
                if (resolutionInput) {
                    resolutionInput.value = window.selectedVideoResolution;
                }
                // Update cost preview with current form state
                recalculateCostAndDuration();
                updateOperationPrices('1280x720');
            });

            // Update file info to show actual duration
            const durationLoading = document.getElementById('durationLoading');
            if (durationLoading) {
                durationLoading.style.display = 'none';
            }

            if (fileInfo) {
                const durationElement = fileInfo.querySelector('.video-duration');
                if (!durationElement) {
                    const durationDiv = document.createElement('div');
                    durationDiv.className = 'small text-muted video-duration';
                    durationDiv.innerHTML = `<i data-feather="clock" style="width: 14px; height: 14px;"></i> مدت: ${formatDuration(duration)}`;
                    fileInfo.querySelector('.alert .flex-grow-1').appendChild(durationDiv);
                    // Re-render feather icons
                    if (typeof feather !== 'undefined') feather.replace();
                } else {
                    durationElement.innerHTML = `<i data-feather="clock" style="width: 14px; height: 14px;"></i> مدت: ${formatDuration(duration)}`;
                    if (typeof feather !== 'undefined') feather.replace();
                }
            }
        }).catch(error => {
            console.error('Error getting video duration:', error);

            // Hide loading state
            const durationLoading = document.getElementById('durationLoading');
            if (durationLoading) {
                durationLoading.style.display = 'none';
            }

            // Fallback to size-based estimation
            const estimatedDuration = estimateVideoDuration(file.size);
            window.selectedVideoDuration = estimatedDuration;
            // Update hidden form input
            const durationInput = document.getElementById('durationInput');
            if (durationInput) {
                durationInput.value = estimatedDuration;
            }
            // Update cost preview with current form state
            recalculateCostAndDuration();

            // Show estimated duration with warning
            if (fileInfo) {
                const durationElement = fileInfo.querySelector('.video-duration');
                if (!durationElement) {
                    const durationDiv = document.createElement('div');
                    durationDiv.className = 'small text-warning video-duration';
                    durationDiv.innerHTML = `<i data-feather="clock" style="width: 14px; height: 14px;"></i> مدت: ~${formatDuration(estimatedDuration)} (تخمینی)`;
                    fileInfo.querySelector('.alert .flex-grow-1').appendChild(durationDiv);
                    if (typeof feather !== 'undefined') feather.replace();
                }
            }
        });

        // Enable form submission
        updateSubmitButton();

        // Show cost preview
        const costPreview = document.getElementById('costPreview');
        const costPlaceholder = document.getElementById('costPlaceholder');
        if (costPreview && costPlaceholder) {
            costPreview.style.display = 'block';
            costPlaceholder.style.display = 'none';
        }
    }
}

// Translation form functionality
function initializeTranslationForm() {
    const operationInputs = document.querySelectorAll('input[name="operation_type"]');
    const sourceLanguage = document.getElementById('source_language');
    const targetLanguage = document.getElementById('target_language');

    operationInputs.forEach(input => {
        input.addEventListener('change', function() {
            recalculateCostAndDuration();
            updateSubmitButton();
        });
    });

    if (sourceLanguage && targetLanguage) {
        sourceLanguage.addEventListener('change', function() {
            recalculateCostAndDuration();
            updateSubmitButton();
        });
        targetLanguage.addEventListener('change', function() {
            recalculateCostAndDuration();
            updateSubmitButton();
        });
    }
}

// Recalculate cost and duration based on current form state
function recalculateCostAndDuration() {
    const fileInput = document.getElementById('video_file');
    const operationType = document.querySelector('input[name="operation_type"]:checked');

    // Only recalculate if we have both a file and operation type selected
    if (fileInput && fileInput.files.length > 0 && operationType) {
        const duration = window.selectedVideoDuration;
        if (duration) {
            updateCostPreview(duration);
        }
    }
}

// Cost calculation and preview
function updateCostPreview(duration) {
    const costPreview = document.getElementById('costPreview');
    const costPlaceholder = document.getElementById('costPlaceholder');
    const videoDuration = document.getElementById('videoDuration');
    const selectedOperation = document.getElementById('selectedOperation');
    const totalCost = document.getElementById('totalCost');
    const remainingCredits = document.getElementById('remainingCredits');
    const sourceLanguage = document.getElementById('source_language');
    const targetLanguage = document.getElementById('target_language');

    if (!costPreview || !costPlaceholder) return;

    const operationType = document.querySelector('input[name="operation_type"]:checked');

    if (duration && operationType) {
        const minutes = Math.max(1, Math.ceil(duration / 60));

        // Get resolution from stored value or default
        const resolution = window.selectedVideoResolution || '720p';
        const costPerMinute = getOperationCost(operationType.value, resolution);
        const cost = minutes * costPerMinute;

        // Update resolution display
        const videoResolution = document.getElementById('videoResolution');
        if (videoResolution) {
            if (resolution.includes('x')) {
                const height = parseInt(resolution.split('x')[1]);
                let resText = resolution;
                if (height <= 720) resText += ' (قیمت پایه)';
                else if (height <= 1080) resText += ' (+1000 تومان/دقیقه)';
                else if (height < 2160) resText += ' (+2000 تومان/دقیقه)';
                else resText += ' (4K - +3000 تومان/دقیقه)';
                videoResolution.textContent = resText;
            } else {
                videoResolution.textContent = resolution;
            }
        }

        // Get current user credits
        const creditsElement = document.querySelector('.user-details .credits, .mobile-credits');
        const userCredits = creditsElement ? parseInt(creditsElement.textContent.replace(/[^0-9]/g, '')) : 0;
        const remaining = userCredits - cost;

        // Update display elements
        if (videoDuration) videoDuration.textContent = formatDuration(duration);
        if (selectedOperation) selectedOperation.textContent = getOperationName(operationType.value);
        if (totalCost) totalCost.textContent = cost.toLocaleString('fa-IR') + ' تومان';
        if (remainingCredits) {
            remainingCredits.textContent = remaining.toLocaleString('fa-IR') + ' تومان';
            remainingCredits.className = remaining >= 0 ? 'text-success' : 'text-danger';
        }

        // Show language information if available
        const languageInfo = document.getElementById('languageInfo');
        if (languageInfo && sourceLanguage && targetLanguage && sourceLanguage.value && targetLanguage.value) {
            const sourceName = sourceLanguage.options[sourceLanguage.selectedIndex].text;
            const targetName = targetLanguage.options[targetLanguage.selectedIndex].text;
            languageInfo.textContent = `${sourceName} → ${targetName}`;
            languageInfo.style.display = 'block';
        } else if (languageInfo) {
            languageInfo.style.display = 'none';
        }

        costPreview.style.display = 'block';
        costPlaceholder.style.display = 'none';

        // Update submit button state based on credits
        const submitBtn = document.getElementById('submitBtn');
        if (submitBtn) {
            if (remaining < 0) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i data-feather="x-circle" class="me-1"></i>موجودی ناکافی';
                submitBtn.className = 'btn btn-danger';
                if (typeof feather !== 'undefined') feather.replace();
            } else {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i data-feather="play" class="me-1"></i>شروع ترجمه';
                submitBtn.className = 'btn btn-primary';
                if (typeof feather !== 'undefined') feather.replace();
            }
        }
    } else {
        costPreview.style.display = 'none';
        costPlaceholder.style.display = 'block';
    }
}

// Helper functions
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

// Get actual video duration using HTML5 video element
function getActualVideoDuration(file) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        video.preload = 'metadata';

        video.onloadedmetadata = function() {
            window.URL.revokeObjectURL(video.src);
            const duration = video.duration;
            if (isFinite(duration) && duration > 0) {
                resolve(duration);
            } else {
                reject(new Error('Invalid video duration'));
            }
        };

        video.onerror = function() {
            window.URL.revokeObjectURL(video.src);
            reject(new Error('Error loading video metadata'));
        };

        video.src = window.URL.createObjectURL(file);
    });
}

// Detect video resolution using HTML5 video element
function detectVideoResolution(file) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        video.preload = 'metadata';

        video.onloadedmetadata = function() {
            const width = video.videoWidth;
            const height = video.videoHeight;
            window.URL.revokeObjectURL(video.src);

            if (width && height) {
                resolve(width + 'x' + height);
            } else {
                reject(new Error('Could not detect video resolution'));
            }
        };

        video.onerror = function() {
            window.URL.revokeObjectURL(video.src);
            reject(new Error('Error loading video for resolution detection'));
        };

        video.src = window.URL.createObjectURL(file);
    });
}

// Update operation prices based on detected video resolution
function updateOperationPrices(resolution) {
    // Parse resolution to get height
    let height = 720;
    if (resolution && typeof resolution === 'string') {
        if (resolution.includes('x')) {
            height = parseInt(resolution.split('x')[1]);
        } else if (resolution.toLowerCase().includes('p')) {
            height = parseInt(resolution.toLowerCase().replace('p', ''));
        }
    }

    // Determine price multiplier based on quality
    let priceNote = 'قیمت پایه';
    let multiplier = 1.0;

    if (height > 1080) {
        multiplier = 2.0;
        priceNote = '۲x قیمت پایه (4K)';
    } else if (height > 720) {
        multiplier = 1.5;
        priceNote = '۱.۵x قیمت پایه (Full HD)';
    }

    // Update all operation price displays
    const baseCosts = document.querySelectorAll('.base-cost');
    baseCosts.forEach(element => {
        const operation = element.dataset.operation;
        if (operation) {
            const basePrice = getBasePrice(operation);
            const adjustedPrice = Math.ceil(basePrice * multiplier);
            element.textContent = adjustedPrice.toLocaleString('fa-IR');
        }
    });

    // Update quality notes
    const qualityNotes = document.querySelectorAll('.quality-note');
    qualityNotes.forEach(note => {
        note.textContent = priceNote;
    });
}

// Get base price for an operation type (in Tomans)
function getBasePrice(operationType) {
    const basePrices = {
        'english_subtitle': 3000,
        'persian_subtitle': 4000,
        'persian_dubbing': 5000,
        'persian_dubbing_english_subtitle': 6000,
        'persian_dubbing_persian_subtitle': 6000
    };
    return basePrices[operationType] || 3000;
}

function estimateVideoDuration(fileSize) {
    // Rough estimation: assume 1MB per minute for average quality video
    const mbSize = fileSize / (1024 * 1024);
    return Math.max(60, mbSize * 60); // Minimum 1 minute
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

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

function updateSubmitButton() {
    // Button is always enabled now, validation happens on click
    return;
}

// Form validation
function initializeFormValidation() {
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Validate file
            const fileInput = document.getElementById('video_file');
            if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
                showNotification('لطفاً یک فایل ویدیو انتخاب کنید', 'error');
                return;
            }

            // Validate operation type
            const operationType = document.querySelector('input[name="operation_type"]:checked');
            if (!operationType) {
                showNotification('لطفاً نوع ترجمه را انتخاب کنید', 'error');
                return;
            }

            // Validate languages
            const sourceLanguage = document.getElementById('source_language');
            const targetLanguage = document.getElementById('target_language');
            if (!sourceLanguage || !sourceLanguage.value || !targetLanguage || !targetLanguage.value) {
                showNotification('لطفاً زبان مبدأ و مقصد را انتخاب کنید', 'error');
                return;
            }

            // Start translation using websocket
            const file = fileInput.files[0];
            startWebsocketUpload(file, operationType.value, sourceLanguage.value, targetLanguage.value);
        });
    }

    // Handle wallet payment form
    const walletForm = document.getElementById('customAmountForm');
    if (walletForm) {
        walletForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const amount = document.getElementById('chargeAmount').value;
            if (!amount) {
                showNotification('لطفاً مبلغ شارژ را وارد کنید', 'error');
                return;
            }

            fetch(`${API_BASE_URL}/wallet/payment`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    amount: parseInt(amount)
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirect to payment gateway
                    window.location.href = data.redirectUrl;
                } else {
                    showNotification(data.message || 'خطا در شروع پرداخت', 'error');
                }
            })
            .catch(error => {
                showNotification('خطا در ارسال درخواست', 'error');
            });
        });
    }
}

// Websocket upload functionality
function startWebsocketUpload(file, operationType, sourceLanguage, targetLanguage) {
    // Show upload progress UI
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const uploadStatus = document.getElementById('uploadStatus');
    const submitBtn = document.getElementById('submitBtn');

    uploadProgress.style.display = 'block';
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i data-feather="upload-cloud" class="me-1"></i>در حال آپلود...';
    if (typeof feather !== 'undefined') feather.replace();

    // Get duration from the form
    const duration = document.getElementById('durationInput').value || 60;

    // Start translation
    fetch(`${API_BASE_URL}/translate/start`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
            videoSize: file.size,
            projectType: operationType,
            useWalletBalance: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const projectId = data.projectId;
            const uploadToken = data.uploadToken;
            const uploadUrl = data.uploadUrl;
            const logsUrl = data.logsUrl;
            const chunkSize = data.chunkSize;

            // Start websocket upload
            uploadViaWebsocket(file, uploadUrl, uploadToken, chunkSize, logsUrl, projectId);
        } else {
            throw new Error(data.message || 'Failed to start translation');
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        showNotification('خطا در شروع آپلود: ' + error.message, 'error');
        uploadProgress.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i data-feather="play" class="me-1"></i>شروع ترجمه';
        if (typeof feather !== 'undefined') feather.replace();
    });
}

// Upload via websocket
function uploadViaWebsocket(file, uploadUrl, uploadToken, chunkSize, logsUrl, projectId) {
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const uploadStatus = document.getElementById('uploadStatus');

    // Create websocket connection for upload
    const wsUrl = uploadUrl.replace('http', 'ws') + `?token=${uploadToken}`;
    const uploadSocket = new WebSocket(wsUrl);

    // Create websocket connection for logs
    const logsSocket = new WebSocket(logsUrl + `?token=${uploadToken}`);

    let totalChunks = Math.ceil(file.size / chunkSize);
    let currentChunk = 0;
    let uploadedBytes = 0;

    // Handle logs messages
    logsSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === 'progress') {
            const progress = Math.round((data.progress || 0) * 100);
            progressBar.style.width = progress + '%';
            progressBar.textContent = progress + '%';
            uploadStatus.textContent = data.message || `در حال آپلود... (${progress}%)`;
        } else if (data.type === 'status') {
            uploadStatus.textContent = data.message || 'در حال پردازش...';
        } else if (data.type === 'error') {
            showNotification('خطا در آپلود: ' + data.message, 'error');
            uploadProgress.style.display = 'none';
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i data-feather="play" class="me-1"></i>شروع ترجمه';
            if (typeof feather !== 'undefined') feather.replace();
        } else if (data.type === 'complete') {
            uploadProgress.style.display = 'none';
            showNotification('ویدیو با موفقیت آپلود شد! پردازش در حال انجام است...', 'success');

            // Start tracking job status
            trackUploadProgress(projectId);

            // Reload page after delay
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 2000);
        }
    };

    // Handle upload socket events
    uploadSocket.onopen = function() {
        uploadStatus.textContent = 'در حال اتصال به سرور...';

        // Send file metadata first
        const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
        uploadSocket.send(JSON.stringify({
            file_extension: fileExtension
        }));

        // Start sending chunks
        sendNextChunk();
    };

    uploadSocket.onerror = function(error) {
        console.error('WebSocket error:', error);
        showNotification('خطا در اتصال به سرور', 'error');
        uploadProgress.style.display = 'none';
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i data-feather="play" class="me-1"></i>شروع ترجمه';
        if (typeof feather !== 'undefined') feather.replace();
    };

    function sendNextChunk() {
        if (currentChunk >= totalChunks) {
            uploadSocket.close();
            return;
        }

        const start = currentChunk * chunkSize;
        const end = Math.min(start + chunkSize, file.size);
        const chunk = file.slice(start, end);

        const reader = new FileReader();
        reader.onload = function(e) {
            const arrayBuffer = e.target.result;
            uploadSocket.send(arrayBuffer);

            currentChunk++;
            uploadedBytes += end - start;

            const progress = Math.round((uploadedBytes / file.size) * 100);
            progressBar.style.width = progress + '%';
            progressBar.textContent = progress + '%';
            uploadStatus.textContent = `آپلود بخش ${currentChunk} از ${totalChunks} (${progress}%)`;

            // Send next chunk
            setTimeout(sendNextChunk, 10); // Small delay to prevent overwhelming the server
        };

        reader.readAsArrayBuffer(chunk);
    }
}

// Progress tracking for uploads
function trackUploadProgress(projectId) {
    const checkStatus = () => {
        fetch(`${API_BASE_URL}/translate/status/${projectId}`, {
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.data.status === 'completed') {
                showNotification('پردازش ویدیو تکمیل شد!', 'success');
                location.reload();
            } else if (data.success && data.data.status === 'failed') {
                showNotification('پردازش ویدیو ناموفق بود', 'error');
            } else if (data.success && data.data.status === 'processing') {
                setTimeout(checkStatus, 5000); // Check again in 5 seconds
            }
        })
        .catch(error => {
            console.error('Error checking job status:', error);
        });
    };

    checkStatus();
}

// Notification system
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