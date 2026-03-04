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

// local filtered state so search doesn't mutate original
let filteredData = null;
let interactionInitialized = false;

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

    // search input listener
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim().toLowerCase();
            if (!query) {
                filteredData = null;
                displayMCQs(mcqData);
                updateStats(mcqData.length);
                return;
            }
            const results = mcqData.filter(mcq => {
                const qtext = mcq.question.toLowerCase();
                if (qtext.includes(query)) return true;
                return mcq.options.some(o => o.toLowerCase().includes(query));
            });
            filteredData = results;
            displayMCQs(results);
            updateStats(results.length);
        });
    }
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
        card.dataset.index = index;
        
        const qLabel = `${index + 1}. `;
        const optionsHtml = mcq.options.map((option, optIndex) => {
            const isCorrect = optIndex === mcq.correct_answer;
            return `<div class="mcq-option ${isCorrect ? 'correct' : ''}" data-qindex="${index}" data-optindex="${optIndex}">${option}</div>`;
        }).join('');
        
        card.innerHTML = `
            <div class="mcq-question" data-qindex="${index}">${qLabel}${mcq.question}</div>
            <div class="mcq-options">${optionsHtml}</div>
        `;
        
        mcqGrid.appendChild(card);
    });

    // attach listeners after rendering
    attachInteractionHandlers();
}

function updateStats(count) {
    let total = mcqData ? mcqData.length : 0;
    let subtitle = 'Review and download your extracted multiple choice questions';
    if (filteredData && filteredData.length !== total) {
        subtitle = `Showing ${count} of ${total} questions`; 
    }
    previewStats.innerHTML = `
        <h2>${count} MCQs Extracted</h2>
        <p>${subtitle}</p>
    `;
}

// ==================== Copy JSON ====================
async function copyJson() {
    try {
        const target = filteredData || mcqData;
        const jsonString = JSON.stringify(target, null, 2);
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
        // If data is filtered/edited only client side, just generate blob instead of API fetch
        if (filteredData) {
            const blob = new Blob([JSON.stringify(filteredData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'mcqs-filtered.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast('Filtered JSON downloaded!', 'success');
            return;
        }

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

// ==================== Interaction helpers ====================
function attachInteractionHandlers() {
    if (interactionInitialized) return;
    interactionInitialized = true;
    // delegate to grid
    mcqGrid.addEventListener('click', onGridClick);
    mcqGrid.addEventListener('dblclick', onGridDblClick);
    mcqGrid.addEventListener('blur', onGridBlur, true);
}

function onGridClick(event) {
    const opt = event.target.closest('.mcq-option');
    if (opt) {
        // toggle correct answer for this question
        const qidx = parseInt(opt.dataset.qindex, 10);
        const oidx = parseInt(opt.dataset.optindex, 10);
        if (!isNaN(qidx) && !isNaN(oidx) && mcqData && mcqData[qidx]) {
            // update data
            mcqData[qidx].correct_answer = oidx;
            // re-render only this card
            displayMCQs(filteredData || mcqData);
            showToast('Correct answer updated', 'success');
        }
    }
}

function onGridDblClick(event) {
    const el = event.target;
    if (el.classList.contains('mcq-question') || el.classList.contains('mcq-option')) {
        el.contentEditable = true;
        el.classList.add('editing');
        el.focus();
    }
}

function onGridBlur(event) {
    const el = event.target;
    if (el.classList.contains('editing')) {
        el.contentEditable = false;
        el.classList.remove('editing');
        // update underlying data
        const qidx = parseInt(el.dataset.qindex, 10);
        if (!isNaN(qidx) && mcqData && mcqData[qidx]) {
            if (el.classList.contains('mcq-question')) {
                // remove leading number and dot
                const txt = el.textContent.replace(/^\d+\.\s*/, '');
                mcqData[qidx].question = txt;
            } else if (el.classList.contains('mcq-option')) {
                const oidx = parseInt(el.dataset.optindex, 10);
                if (!isNaN(oidx)) {
                    mcqData[qidx].options[oidx] = el.textContent;
                }
            }
            showToast('Change saved locally', 'info');
        }
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
