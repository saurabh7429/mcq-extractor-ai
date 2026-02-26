/**
 * preview.js - Handle preview page functionality
 */

// Get API URL from config
const API_BASE_URL = window.API_BASE_URL || '';

// ==================== DOM Elements ====================
const previewStats = document.getElementById('previewStats');
const loadingContainer = document.getElementById('loadingContainer');
const errorContainer = document.getElementById('errorContainer');
const errorText = document.getElementById('errorText');
const mcqGrid = document.getElementById('mcqGrid');
const copyJsonBtn = document.getElementById('copyJsonBtn');
const downloadJsonBtn = document.getElementById('downloadJsonBtn');
const backBtn = document.getElementById('backBtn');

// ==================== State ====================
let currentFileId = null;
let mcqData = null;

// ==================== Event Listeners ====================
document.addEventListener('DOMContentLoaded', init);

function init() {
    // Get file_id from sessionStorage
    currentFileId = sessionStorage.getItem('currentFileId');
    
    if (!currentFileId) {
        showError('No file ID found. Please upload a file first.');
        return;
    }
    
    // Load MCQ data
    loadMCQs();
    
    // Setup button listeners
    copyJsonBtn.addEventListener('click', copyJson);
    downloadJsonBtn.addEventListener('click', downloadJson);
    backBtn.addEventListener('click', () => {
        window.location.href = 'index.html';
    });
}

// ==================== Load MCQs ====================
async function loadMCQs() {
    try {
        // Show loading
        showLoadingState();
        
        // Fetch MCQs from API
        const response = await fetch(API_BASE_URL + '/api/extract/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_id: currentFileId })
        });
        
        const data = await response.json();
        
        if (!response.ok || data.status === 'error') {
            throw new Error(data.message || 'Failed to load MCQs');
        }
        
        mcqData = data.mcqs;
        
        // Display MCQs
        displayMCQs(mcqData);
        updateStats(mcqData.length);
        
    } catch (error) {
        console.error('Error loading MCQs:', error);
        showError(error.message || 'Failed to load MCQs. Please try again.');
    }
}

function showLoadingState() {
    loadingContainer.classList.remove('hidden');
    mcqGrid.classList.add('hidden');
    errorContainer.classList.add('hidden');
}

function hideLoadingState() {
    loadingContainer.classList.add('hidden');
    mcqGrid.classList.remove('hidden');
}

function showError(message) {
    loadingContainer.classList.add('hidden');
    mcqGrid.classList.add('hidden');
    errorContainer.classList.remove('hidden');
    errorText.textContent = message;
}

// ==================== Display MCQs ====================
function displayMCQs(mcqs) {
    hideLoadingState();
    
    mcqGrid.innerHTML = '';
    
    mcqs.forEach((mcq, index) => {
        const card = document.createElement('div');
        card.className = 'mcq-card';
        
        const optionsHtml = mcq.options.map((option, optIndex) => {
            const isCorrect = optIndex === mcq.correct_answer;
            return `<div class="mcq-option ${isCorrect ? 'correct' : ''}">${option}</div>`;
        }).join('');
        
        card.innerHTML = `
            <div class="mcq-question">${index + 1}. ${mcq.question}</div>
            <div class="mcq-options">${optionsHtml}</div>
        `;
        
        mcqGrid.appendChild(card);
    });
}

function updateStats(count) {
    previewStats.innerHTML = `
        <h2>${count} MCQs Extracted</h2>
        <p>Review and download your extracted multiple choice questions</p>
    `;
}

// ==================== Copy JSON ====================
async function copyJson() {
    try {
        const jsonString = JSON.stringify(mcqData, null, 2);
        await navigator.clipboard.writeText(jsonString);
        
        showToast('JSON copied to clipboard!', 'success');
    } catch (error) {
        console.error('Error copying JSON:', error);
        showToast('Failed to copy JSON', 'error');
    }
}

// ==================== Download JSON ====================
async function downloadJson() {
    try {
        const response = await fetch(API_BASE_URL + '/api/download/json', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_id: currentFileId })
        });
        
        if (!response.ok) {
            throw new Error('Failed to download JSON');
        }
        
        // Get filename from response headers
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'mcqs.json';
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="(.+)"/);
            if (match) {
                filename = match[1];
            }
        }
        
        // Download file
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('JSON downloaded successfully!', 'success');
    } catch (error) {
        console.error('Error downloading JSON:', error);
        showToast('Failed to download JSON', 'error');
    }
}

// ==================== Toast ====================
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
