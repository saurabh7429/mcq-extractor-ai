/**
 * preview.js - Handle MCQ preview functionality with export options
 */

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

const EXPORT_FORMATS = [
    { id: 'json', name: 'JSON', ext: 'json', icon: '&#128459;' },
    { id: 'csv', name: 'CSV', ext: 'csv', icon: '&#128202;' },
    { id: 'txt', name: 'TXT', ext: 'txt', icon: '&#128221;' },
    { id: 'markdown', name: 'Markdown', ext: 'md', icon: '&#128196;' },
    { id: 'html', name: 'HTML', ext: 'html', icon: '&#127760;' },
    { id: 'xml', name: 'XML', ext: 'xml', icon: '&#128240;' },
    { id: 'yaml', name: 'YAML', ext: 'yaml', icon: '&#128459;' },
    { id: 'sql', name: 'SQL', ext: 'sql', icon: '&#128451;' },
    { id: 'aiken', name: 'Aiken', ext: 'txt', icon: '&#9989;' },
    { id: 'gift', name: 'GIFT', ext: 'txt', icon: '&#127873;' },
    { id: 'excel', name: 'Excel', ext: 'xlsx', icon: '&#128200;' }
];

let currentMcqs = [];
let currentFileId = null;

document.addEventListener('DOMContentLoaded', function() {
    currentFileId = sessionStorage.getItem('currentFileId');
    const fileName = sessionStorage.getItem('currentFileName');
    
    if (!currentFileId) {
        showError('No file ID found. Please upload a file first.');
        return;
    }
    
    if (fileName) {
        const fileNameEl = document.getElementById('fileName');
        if (fileNameEl) fileNameEl.textContent = fileName;
    }
    
    loadMcqs(currentFileId);
    setupExportDropdown();
});

function setupExportDropdown() {
    // Toggle dropdown visibility
    const exportFormatBtn = document.getElementById('exportFormatBtn');
    const exportMenu = document.getElementById('exportMenu');
    
    if (exportFormatBtn && exportMenu) {
        exportFormatBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            exportMenu.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!exportFormatBtn.contains(e.target) && !exportMenu.contains(e.target)) {
                exportMenu.classList.remove('show');
            }
        });
    }
    
    // Set up export option click handlers
    const exportOptions = document.querySelectorAll('.export-option');
    exportOptions.forEach(function(option) {
        option.addEventListener('click', function() {
            const format = this.getAttribute('data-format');
            if (format) {
                downloadInFormat(format);
                // Close dropdown after selection
                if (exportMenu) exportMenu.classList.remove('show');
            }
        });
    });
}

async function downloadInFormat(format) {
    if (!currentFileId) return;
    
    try {
        const response = await fetch(API_BASE_URL + '/download/export/' + format + '/' + currentFileId);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Export failed');
        }
        
        const blob = await response.blob();
        const formatInfo = EXPORT_FORMATS.find(function(f) { return f.id === format; });
        const ext = formatInfo ? formatInfo.ext : format;
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = currentFileId + '.' + ext;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast((formatInfo ? formatInfo.name : format.toUpperCase()) + ' downloaded!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showToast('Failed to export: ' + error.message, 'error');
    }
}

async function loadMcqs(fileId) {
    try {
        showLoading();
        const response = await fetch(API_BASE_URL + '/extract/' + fileId);
        
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

function displayMcqs(mcqs) {
    hideLoading();
    
    if (!mcqs || mcqs.length === 0) {
        showError('No MCQs found in the document.');
        return;
    }
    
    const mcqGrid = document.getElementById('mcqGrid');
    const previewStats = document.getElementById('previewStats');
    
    if (previewStats) {
        previewStats.innerHTML = '<h2 class="preview-stats-title">' + mcqs.length + ' MCQs Extracted</h2>';
    }
    
    const mcqCountEl = document.getElementById('mcqCount');
    if (mcqCountEl) mcqCountEl.textContent = mcqs.length + ' Questions';
    
    const mcqSection = document.getElementById('mcqSection');
    if (mcqSection) mcqSection.classList.remove('hidden');
    
    if (mcqGrid) mcqGrid.innerHTML = '';
    
    mcqs.forEach(function(mcq, index) {
        const card = createMcqCard(mcq, index + 1);
        if (mcqGrid) mcqGrid.appendChild(card);
    });
}

function createMcqCard(mcq, number) {
    const card = document.createElement('div');
    card.className = 'mcq-card';
    
    const options = Array.isArray(mcq.options) ? mcq.options : 
                   (typeof mcq.options === 'string' ? JSON.parse(mcq.options) : []);
    
    const correctIndex = mcq.correct_answer !== undefined ? mcq.correct_answer : -1;
    
    const optionLetters = ['A', 'B', 'C', 'D'];
    const optionsHtml = options.map(function(option, idx) {
        const isCorrect = idx === correctIndex;
        return '<div class="mcq-option ' + (isCorrect ? 'correct' : '') + '">' +
            '<span class="mcq-option-letter">' + optionLetters[idx] + '</span>' +
            '<span class="mcq-option-text">' + escapeHtml(option) + '</span>' +
            '</div>';
    }).join('');
    
    card.innerHTML = '<div class="mcq-number">' + number + '</div>' +
        '<div class="mcq-question">' + escapeHtml(mcq.question || '') + '</div>' +
        '<div class="mcq-options">' + optionsHtml + '</div>';
    
    return card;
}

function showLoading() {
    const loadingContainer = document.getElementById('loadingContainer');
    const mcqGrid = document.getElementById('mcqGrid');
    const errorContainer = document.getElementById('errorContainer');
    
    if (loadingContainer) loadingContainer.classList.remove('hidden');
    if (mcqGrid) mcqGrid.classList.add('hidden');
    if (errorContainer) errorContainer.classList.add('hidden');
}

function hideLoading() {
    const loadingContainer = document.getElementById('loadingContainer');
    const mcqGrid = document.getElementById('mcqGrid');
    
    if (loadingContainer) loadingContainer.classList.add('hidden');
    if (mcqGrid) mcqGrid.classList.remove('hidden');
}

function showError(message) {
    const loadingContainer = document.getElementById('loadingContainer');
    const mcqGrid = document.getElementById('mcqGrid');
    const errorContainer = document.getElementById('errorContainer');
    const errorText = document.getElementById('errorText');
    
    if (loadingContainer) loadingContainer.classList.add('hidden');
    if (mcqGrid) mcqGrid.classList.add('hidden');
    if (errorContainer) {
        errorContainer.classList.remove('hidden');
        if (errorText) errorText.textContent = message;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    
    let iconSvg = '';
    if (type === 'success') {
        iconSvg = '<svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>';
    } else if (type === 'error') {
        iconSvg = '<svg class="toast-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>';
    }
    
    toast.innerHTML = iconSvg + '<span class="toast-message">' + escapeHtml(message) + '</span>';
    toastContainer.appendChild(toast);
    
    setTimeout(function() {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
}

window.MCQPreview = { loadMcqs: loadMcqs, displayMcqs: displayMcqs, downloadInFormat: downloadInFormat };