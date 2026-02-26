/**
 * status.js - Handle loading states and status messages
 */

// Function to show loading state
function showLoading(title, subtitle) {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const loadingTitle = document.getElementById('loadingTitle');
    const loadingSubtitle = document.getElementById('loadingSubtitle');
    const progressBar = document.getElementById('progressBar');
    
    if (loadingSpinner) {
        loadingTitle.textContent = title;
        loadingSubtitle.textContent = subtitle;
        progressBar.style.width = '0%';
        
        loadingSpinner.classList.remove('hidden');
        
        // Animate progress bar
        animateProgressBar();
    }
}

// Function to hide loading state
function hideLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) {
        loadingSpinner.classList.add('hidden');
    }
}

// Animate progress bar
function animateProgressBar() {
    const progressBar = document.getElementById('progressBar');
    if (!progressBar) return;
    
    let width = 0;
    const interval = setInterval(() => {
        if (width >= 90) {
            clearInterval(interval);
        } else {
            width += Math.random() * 10;
            if (width > 90) width = 90;
            progressBar.style.width = width + '%';
        }
    }, 500);
}

// Function to show status message
function showStatusMessage(message, type = 'info') {
    const statusMessages = document.getElementById('statusMessages');
    if (!statusMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `status-message ${type}`;
    messageDiv.innerHTML = `
        <div class="status-icon">
            ${type === 'success' ? '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>' : ''}
            ${type === 'error' ? '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>' : ''}
        </div>
        <div class="status-text">
            <strong>${message}</strong>
        </div>
    `;
    
    statusMessages.appendChild(messageDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Export functions globally
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.showStatusMessage = showStatusMessage;
window.showToast = showToast;
