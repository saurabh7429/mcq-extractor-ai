/**
 * status.js - Handle status messages and notifications
 */

// ==================== Status Messages ====================

const statusMessages = {
    reading: {
        title: 'Reading PDF...',
        subtitle: 'Extracting text from your PDF document'
    },
    extracting: {
        title: 'Extracting MCQs...',
        subtitle: 'Using AI to analyze and extract questions'
    },
    saving: {
        title: 'Saving to database...',
        subtitle: 'Storing your MCQs securely'
    },
    complete: {
        title: 'Extraction Complete!',
        subtitle: 'Your MCQs are ready to view'
    },
    error: {
        title: 'Error',
        subtitle: 'Something went wrong'
    }
};

// ==================== Status Display Functions ====================

function showStatus(type, message = null) {
    const statusMessagesContainer = document.getElementById('statusMessages');
    const statusConfig = statusMessages[type] || statusMessages.error;
    
    const statusDiv = document.createElement('div');
    statusDiv.className = `status-message ${type}`;
    statusDiv.innerHTML = `
        <div class="status-icon">
            ${getStatusIcon(type)}
        </div>
        <div class="status-text">
            <strong>${message || statusConfig.title}</strong>
            <small>${statusConfig.subtitle}</small>
        </div>
    `;
    
    statusMessagesContainer.appendChild(statusDiv);
    
    // Auto-scroll to status
    statusDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    return statusDiv;
}

function clearStatus() {
    const statusMessagesContainer = document.getElementById('statusMessages');
    statusMessagesContainer.innerHTML = '';
}

function getStatusIcon(type) {
    const icons = {
        info: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>`,
        success: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>`,
        error: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>`,
        warning: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>`
    };
    
    return icons[type] || icons.info;
}

// ==================== Toast Notifications ====================

function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function showSuccessToast(message, duration = 3000) {
    showToast(message, 'success', duration);
}

function showErrorToast(message, duration = 5000) {
    showToast(message, 'error', duration);
}

function showInfoToast(message, duration = 3000) {
    showToast(message, 'info', duration);
}

// ==================== Progress Tracking ====================

function updateProgress(percentage, message = '') {
    const progressBar = document.getElementById('progressBar');
    if (progressBar) {
        progressBar.style.width = `${Math.min(percentage, 100)}%`;
    }
}

function resetProgress() {
    updateProgress(0);
}

// Export for use in other modules
window.MCQStatus = {
    showStatus,
    clearStatus,
    showToast,
    showSuccessToast,
    showErrorToast,
    showInfoToast,
    updateProgress,
    resetProgress,
    statusMessages
};
