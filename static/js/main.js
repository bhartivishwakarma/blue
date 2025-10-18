// static/js/main.js
class BlueCollarApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFormEnhancements();
        this.setupAutoSave();
    }

    setupEventListeners() {
        // Profession selection
        this.setupProfessionSelection();
        
        // Template selection
        this.setupTemplateSelection();
        
        // Form validation
        this.setupFormValidation();
        
        // Auto-advance OTP
        this.setupOTPAutoFill();
        
        // File upload enhancements
        this.setupFileUploads();
    }

    setupProfessionSelection() {
        const professionCards = document.querySelectorAll('.profession-card');
        professionCards.forEach(card => {
            card.addEventListener('click', function() {
                professionCards.forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                
                const radio = this.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                }
            });
        });
    }

    setupTemplateSelection() {
        const templateCards = document.querySelectorAll('.template-card');
        templateCards.forEach(card => {
            card.addEventListener('click', function() {
                templateCards.forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                
                const radio = this.querySelector('input[type="radio"]');
                if (radio) {
                    radio.checked = true;
                }
            });
        });
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const requiredFields = this.querySelectorAll('[required]');
                let isValid = true;
                
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        isValid = false;
                        this.showFieldError(field, 'This field is required');
                    } else {
                        this.clearFieldError(field);
                    }
                });
                
                // Email validation
                const emailFields = this.querySelectorAll('input[type="email"]');
                emailFields.forEach(field => {
                    if (field.value && !this.isValidEmail(field.value)) {
                        isValid = false;
                        this.showFieldError(field, 'Please enter a valid email address');
                    }
                });
                
                // Mobile validation
                const mobileFields = this.querySelectorAll('input[type="tel"]');
                mobileFields.forEach(field => {
                    if (field.value && !this.isValidMobile(field.value)) {
                        isValid = false;
                        this.showFieldError(field, 'Please enter a valid 10-digit mobile number');
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    this.showToast('Please fix the errors in the form', 'error');
                }
            });
        });
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        field.style.borderColor = 'var(--error)';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            color: var(--error);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        `;
        
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.style.borderColor = '';
        
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidMobile(mobile) {
        const mobileRegex = /^[0-9]{10}$/;
        return mobileRegex.test(mobile);
    }

    setupOTPAutoFill() {
        const otpInput = document.getElementById('otp');
        if (otpInput) {
            // Simulate auto-fill for demo
            setTimeout(() => {
                if (!otpInput.value) {
                    otpInput.value = '123456';
                    this.showToast('OTP auto-filled for demo', 'info');
                }
            }, 3000);

            // Auto-submit when complete
            otpInput.addEventListener('input', function() {
                if (this.value.length === 6) {
                    this.form.submit();
                }
            });
        }
    }

    setupFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    const maxSize = 16 * 1024 * 1024; // 16MB
                    if (file.size > maxSize) {
                        this.showToast('File size must be less than 16MB', 'error');
                        this.value = '';
                        return;
                    }
                    
                    const fileName = file.name;
                    const uploadArea = this.parentElement;
                    const placeholder = uploadArea.querySelector('.upload-placeholder');
                    
                    if (placeholder) {
                        placeholder.innerHTML = `
                            <i class="fas fa-file-alt upload-icon"></i>
                            <p>${fileName}</p>
                            <small>Click to change file</small>
                        `;
                        uploadArea.style.borderColor = 'var(--success)';
                    }
                    
                    this.showToast('File selected successfully', 'success');
                }
            });
        });
    }

    setupAutoSave() {
        // Auto-save form data to localStorage
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // Load saved data
                const savedValue = localStorage.getItem(input.name);
                if (savedValue && !input.value) {
                    input.value = savedValue;
                }
                
                // Save on input
                input.addEventListener('input', () => {
                    localStorage.setItem(input.name, input.value);
                });
            });
        });
    }

    showToast(message, type = 'info') {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)} toast-icon"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close">&times;</button>
        `;
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--white);
            padding: 1rem 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            border-left: 4px solid var(--${type});
            display: flex;
            align-items: center;
            gap: 1rem;
            z-index: 10000;
            animation: slideInRight 0.3s ease;
            max-width: 400px;
        `;
        
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => toast.remove());
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Utility method for making API calls
    async apiCall(endpoint, data = {}) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            this.showToast('Network error. Please try again.', 'error');
            throw error;
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    window.blueCollarApp = new BlueCollarApp();
});

// Utility functions
function formatPhoneNumber(phone) {
    return phone.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
}

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

// Service Worker Registration for offline functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}