/**
 * Statistics Module - MCQ Extractor AI
 * Handles fetching and updating statistics with anti-spam protection
 */

// Dynamic API_BASE_URL based on deployment
const API_BASE_URL = (function() {
    const hostname = window.location.hostname;
    
    // Localhost or 127.0.0.1
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return '/api';
    }
    // GitHub Pages - redirect to Render backend
    if (hostname.includes('github.io')) {
        return 'https://mcq-extractor-ai.onrender.com/api';
    }
    // Render - same origin
    return '/api';
})();

const StatsManager = {
    // API base URL - dynamically set based on deployment
    API_BASE: API_BASE_URL + '/stats',
    
    /**
     * Fetch current statistics from server
     */
    async fetchStats() {
        try {
            const response = await fetch(this.API_BASE);
            if (!response.ok) throw new Error('Failed to fetch stats');
            return await response.json();
        } catch (error) {
            console.error('Error fetching stats:', error);
            return { views: 0, likes: 0, dislikes: 0 };
        }
    },
    
    /**
     * Submit a like vote
     */
    async submitLike() {
        // Check anti-spam
        if (this.hasLiked()) {
            this.showToast('You have already liked!', 'info');
            return false;
        }
        
        try {
            const response = await fetch(`${this.API_BASE}/like`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) throw new Error('Failed to submit like');
            
            const data = await response.json();
            
            // Set localStorage to prevent spam
            localStorage.setItem('liked', 'true');
            
            this.updateLikeButtonState(true);
            this.showToast('Thanks for your feedback!', 'success');
            
            return data;
        } catch (error) {
            console.error('Error submitting like:', error);
            this.showToast('Failed to submit like', 'error');
            return null;
        }
    },
    
    /**
     * Submit a dislike vote
     */
    async submitDislike() {
        // Check anti-spam
        if (this.hasDisliked()) {
            this.showToast('You have already disliked!', 'info');
            return false;
        }
        
        try {
            const response = await fetch(`${this.API_BASE}/dislike`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) throw new Error('Failed to submit dislike');
            
            const data = await response.json();
            
            // Set localStorage to prevent spam
            localStorage.setItem('disliked', 'true');
            
            this.updateDislikeButtonState(true);
            this.showToast('Thanks for your feedback!', 'success');
            
            return data;
        } catch (error) {
            console.error('Error submitting dislike:', error);
            this.showToast('Failed to submit dislike', 'error');
            return null;
        }
    },
    
    /**
     * Check if user has already liked
     */
    hasLiked() {
        return localStorage.getItem('liked') === 'true';
    },
    
    /**
     * Check if user has already disliked
     */
    hasDisliked() {
        return localStorage.getItem('disliked') === 'true';
    },
    
    /**
     * Update the displayed statistics
     */
    updateDisplay(stats) {
        const viewsEl = document.getElementById('statsViews');
        const likesEl = document.getElementById('statsLikes');
        const dislikesEl = document.getElementById('statsDislikes');
        
        if (viewsEl) viewsEl.textContent = this.formatNumber(stats.views || 0);
        if (likesEl) likesEl.textContent = this.formatNumber(stats.likes || 0);
        if (dislikesEl) dislikesEl.textContent = this.formatNumber(stats.dislikes || 0);
    },
    
    /**
     * Update like button state (disabled after voting)
     */
    updateLikeButtonState(disliked = false) {
        const likeBtn = document.getElementById('likeBtn');
        if (likeBtn) {
            likeBtn.disabled = true;
            likeBtn.classList.add('voted');
            likeBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Liked
            `;
        }
    },
    
    /**
     * Update dislike button state (disabled after voting)
     */
    updateDislikeButtonState(disliked = false) {
        const dislikeBtn = document.getElementById('dislikeBtn');
        if (dislikeBtn) {
            dislikeBtn.disabled = true;
            dislikeBtn.classList.add('voted');
            dislikeBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Disliked
            `;
        }
    },
    
    /**
     * Initialize stats display and button states
     */
    async init() {
        // Fetch and display current stats
        const stats = await this.fetchStats();
        this.updateDisplay(stats);
        
        // Update button states based on localStorage
        if (this.hasLiked()) {
            this.updateLikeButtonState();
        }
        if (this.hasDisliked()) {
            this.updateDislikeButtonState();
        }
        
        // Attach event listeners to like/dislike buttons
        this.attachEventListeners();
    },
    
    /**
     * Attach event listeners to buttons
     */
    attachEventListeners() {
        const likeBtn = document.getElementById('likeBtn');
        const dislikeBtn = document.getElementById('dislikeBtn');
        
        if (likeBtn) {
            likeBtn.addEventListener('click', () => this.submitLike());
        }
        
        if (dislikeBtn) {
            dislikeBtn.addEventListener('click', () => this.submitDislike());
        }
    },
    
    /**
     * Format large numbers (e.g., 1000 -> 1K)
     */
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    },
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = '';
        if (type === 'success') {
            icon = '<svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#10b981"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
        } else if (type === 'error') {
            icon = '<svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#ef4444"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>';
        } else {
            icon = '<svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="#4f46e5"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
        }
        
        toast.innerHTML = `
            ${icon}
            <span class="toast-message">${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    StatsManager.init();
});

