/**
 * preview.js - Handle MCQ preview functionality
 */

// Dynamic API_BASE_URL based on deployment
const API_BASE_URL = (function() {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return '/api';
    }
    if (hostname.includes('github.io')) {
        return 'https://mcq-extractor-ai.onrender.com/api';
    }
    return '/api';
})();

// DOM Elements
const mcqGrid = document.getElementById('mcqGrid');
const previewStats = document.getElementById('previewStats');
const loadingContainer = document.getElementById('loadingContainer');
const errorContainer = document.getElementById('errorContainer');
const errorText = document.getElementById('errorText');
const copyJsonBtn = document.getElementById('copyJsonBtn');
const downloadJsonBtn = document.getElementById('downloadJsonBtn');
const backBtn = document.getElementById('backBtn');
const exportFormatBtn = document.getElementById('exportFormatBtn');
const exportMenu = document.getElementById('exportMenu');

// State
let currentMcqs = [];
let currentFileId = null;

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', () => {
    // Get file_id from sessionStorage
    currentFileId = sessionStorage.getItem('currentFileId');
    const fileName = sessionStorage.getItem('currentFileName');
    
    if (!currentFileId) {
        showError('No file ID found. Please upload a file first.');
        return;
    }
    
    // Update filename display
    if (fileName) {
        const fileNameEl = document.getElementById('fileName');
        if (fileNameEl) {
            fileNameEl.textContent = fileName;
        }
    }
    
    // Load MCQs
    loadMcqs(currentFileId);
    
    // Setup button listeners
    setupButtonListeners();
});

// ==================== Button Listeners ====================

function setupButtonListeners() {
    // Copy JSON button
    if (copyJsonBtn) {
        copyJsonBtn.addEventListener('click', copyJsonToClipboard);
    }
    
    // Download JSON button
    if (downloadJsonBtn) {
        downloadJsonBtn.addEventListener('click', downloadJson);
    }
    
    // Back button
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            window.location.href = 'index.html';
        });
    }
    
    // Export format button and menu
    if (exportFormatBtn && exportMenu) {
        exportFormatBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            exportMenu.classList.toggle('show');
        });
        
        // Handle export option clicks
        const exportOptions = exportMenu.querySelectorAll('.export-option');
        exportOptions.forEach(option => {
            option.addEventListener('click', async (e) => {
                const format = e.currentTarget.dataset.format;
                await exportToFormat(format);
                exportMenu.classList.remove('show');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!exportFormatBtn.contains(e.target) && !exportMenu.contains(e.target)) {
                exportMenu.classList.remove('show');
            }
        });
    }
}

// ==================== Export Functions ====================

async function exportToFormat(format) {
    if (!currentFileId) {
        showToast('No file ID found', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/download/export/${format}/${currentFileId}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to export');
        }
        
        // Get the blob from response
        const blob = await response.blob();
        
        // Get filename from content-disposition header or create default
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `${currentFileId}.${format}`;
        if (contentDisposition) {
            const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match) {
                filename = match[1].replace(/['"]/g, '');
            }
        }
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        const formatUpper = format.toUpperCase();
        showToast(`${formatUpper} file downloaded successfully!`, 'success');
        
    } catch (error) {
        console.error('Export error:', error);
        showToast(`Failed to export: ${error.message}`, 'error');
    }
}

// ==================== Load MCQs ====================

async function loadMcqs(fileId) {
    try {
        showLoading();
        
        // Fetch MCQs from extract endpoint
        const response = await fetch(`${API_BASE_URL}/extract/${fileId}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to load MCQs');
        }
        
        const data = await response.json();
        
        if (data.mcqs && Array.isArray(data.mcqs)) {
            currentMcqs = data.mcqs;
            displayMcqs(currentMcqs);
        } else {
            throw new Error('No MCQs found in response');
        }
        
    } catch (error) {
        console.error('Load MCQs error:', error);
        showError(error.message || 'Failed to load MCQs. Please try again.');
    }
}

// ==================== Display MCQs ====================

function displayMcqs(mcqs) {
    hideLoading();
    
    if (!mcqs || mcqs.length === 0) {
        showError('No MCQs found in the document.');
        return;
    }
    
    // Update stats
    if (previewStats) {
        previewStats.innerHTML = `
            <h2 class="preview-stats-title">${mcqs.length} MCQs Extracted</h2>
            <p class="preview-stats-subtitle">From: ${sessionStorage.getItem('currentFileName') || 'Unknown'}</p>
        `;
    }
    
    // Update MCQ count in section header
    const mcqCountEl = document.getElementById('mcqCount');
    if (mcqCountEl) {
        mcqCountEl.textContent = `${mcqs.length} Questions`;
    }
    
    // Show MCQ section
    const mcqSection = document.getElementById('mcqSection');
    if (mcqSection) {
        mcqSection.classList.remove('hidden');
    }
    
    // Clear grid
    mcqGrid.innerHTML = '';
    
    // Create MCQ cards
    mcqs.forEach((mcq, index) => {
        const card = createMcqCard(mcq, index + 1);
        mcqGrid.appendChild(card);
    });
}

function createMcqCard(mcq, number) {
    const card = document.createElement('div');
    card.className = 'mcq-card';
    
    // Get options as array
    const options = Array.isArray(mcq.options) ? mcq.options : 
                   (typeof mcq.options === 'string' ? JSON.parse(mcq.options) : []);
    
    // Determine correct answer index
    const correctIndex = mcq.correct_answer !== undefined ? mcq.correct_answer : -1;
    
    // Create options HTML
    const optionLetters = ['A', 'B', 'C', 'D'];
    const optionsHtml = options.map((option, idx) => {
        const isCorrect = idx === correctIndex;
        return `
            <div class="mcq-option ${isCorrect ? 'correct' : ''}">
                <span class="mcq-option-letter">${optionLetters[idx]}</span>
                <span class="mcq-option-text">${escapeHtml(option)}</span>
            </div>
        `;
    }).join('');
    
    card.innerHTML = `
        <div class="mcq-number">${number}</div>
        <div class="mcq-question">${escapeHtml(mcq.question || '')}</div>
        <div class="mcq-options">
            ${optionsHtml}
        </div>
    `;
    
    return card;
}

// ==================== Copy to Clipboard ====================

async function copyJsonToClipboard() {
    try {
        const jsonString = JSON.stringify(currentMcqs, null, 2);
        await navigator.clipboard.writeText(jsonString);
        
        showToast('JSON copied to clipboard!', 'success');
        
        // Update button text temporarily
        const originalText = copyJsonBtn.innerHTML;
        copyJsonBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Copied!
        `;
        
        setTimeout(() => {
            copyJsonBtn.innerHTML = originalText;
        }, 2000);
        
    } catch (error) {
        console.error('Copy error:', error);
        showToast('Failed to copy to clipboard', 'error');
    }
}

// ==================== Download JSON ====================

function downloadJson() {
    try {
        const jsonString = JSON.stringify(currentMcqs, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentFileId || 'mcqs'}.json`;
        document.body.appendChild(a);
        a.click();
        
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('JSON file downloaded!', 'success');
        
    } catch (error) {
        console.error('Download error:', error);
        showToast('Failed to download JSON', 'error');
    }
}

// ==================== Loading & Error States ====================

function showLoading() {
    if (loadingContainer) loadingContainer.classList.remove('hidden');
    if (mcqGrid) mcqGrid.classList.add('hidden');
    if (errorContainer) errorContainer.classList.add('hidden');
}

function hideLoading() {
    if (loadingContainer) loadingContainer.classList.add('hidden');
    if (mcqGrid) mcqGrid.classList.remove('hidden');
}

function showError(message) {
    if (loadingContainer) loadingContainer.classList.add('hidden');
    if (mcqGrid) mcqGrid.classList.add('hidden');
    if (errorContainer) {
        errorContainer.classList.remove('hidden');
        if (errorText) errorText.textContent = message;
    }
}

// ==================== Utility Functions ====================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let iconSvg = '';
    if (type === 'success') {
        iconSvg = '<svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
    } else if (type === 'error') {
        iconSvg = '<svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>';
    } else {
        iconSvg = '<svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
    }
    
    toast.innerHTML = `${iconSvg}<span class="toast-message">${escapeHtml(message)}</span>`;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Export for use in other modules
window.MCQPreview = {
    loadMcqs,
    displayMcqs,
    copyJsonToClipboard,
    downloadJson
};
