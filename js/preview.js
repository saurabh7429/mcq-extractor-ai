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

// Get base path for redirects (works with sub-directory hosting like GitHub Pages)
const BASE_PATH = (function() {
    const path = window.location.pathname;
    if (path === '/' || path === '') return '/';
    // Remove trailing slash if present
    let base = path.endsWith('/') ? path.slice(0, -1) : path;
    // Get the repo name from the path
    const parts = base.split('/');
    // Check if the second part looks like a repo name (not a file like preview.html)
    // Repo names typically don't have dots and are not .html files
    if (parts.length > 1 && parts[1] && !parts[1].endsWith('.html') && parts[1] !== '') {
        return '/' + parts[1] + '/';
    }
    return '/';
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
    { id: 'excel', name: 'Excel', ext: 'xlsx', icon: '&#128200;' },
    // New print-ready formats
    { id: 'question_pdf', name: 'Question Paper PDF', ext: 'pdf', icon: '&#128196;' },
    { id: 'answer_key_pdf', name: 'Answer Key PDF', ext: 'pdf', icon: '&#128273;' },
    { id: 'omr_pdf', name: 'OMR Sheet PDF', ext: 'pdf', icon: '&#128203;' },
    { id: 'tabular_pdf', name: 'Tabular PDF', ext: 'pdf', icon: '&#128202;' },
    { id: 'docx', name: 'DOCX Question Paper', ext: 'docx', icon: '&#128462;' }
];

let currentMcqs = [];
let currentFileId = null;
let selectedQuestions = new Set(); // Track selected question indices
let removedQuestions = new Set(); // Track removed question indices
let quizType = 'all'; // 'all' or 'random'
let selectedRandomCount = 0;

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
    setupButtonHandlers();
});

function setupButtonHandlers() {
    // Copy JSON button
    const copyJsonBtn = document.getElementById('copyJsonBtn');
    if (copyJsonBtn) {
        copyJsonBtn.addEventListener('click', async function() {
            try {
                const response = await fetch(API_BASE_URL + '/extract/' + currentFileId);
                if (!response.ok) throw new Error('Failed to load MCQs');
                const data = await response.json();
                if (data.mcqs) {
                    await navigator.clipboard.writeText(JSON.stringify(data.mcqs, null, 2));
                    showToast('JSON copied to clipboard!', 'success');
                }
            } catch (error) {
                console.error('Copy error:', error);
                showToast('Failed to copy: ' + error.message, 'error');
            }
        });
    }
    
    // Download JSON button
    const downloadJsonBtn = document.getElementById('downloadJsonBtn');
    if (downloadJsonBtn) {
        downloadJsonBtn.addEventListener('click', async function() {
            try {
                const response = await fetch(API_BASE_URL + '/download/' + currentFileId);
                if (!response.ok) throw new Error('Failed to download');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = currentFileId + '.json';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                showToast('JSON downloaded!', 'success');
            } catch (error) {
                console.error('Download error:', error);
                showToast('Failed to download: ' + error.message, 'error');
            }
        });
    }
    
    // Back button (Upload More) - Use BASE_PATH for redirect
    const backBtn = document.getElementById('backBtn');
    if (backBtn) {
        backBtn.addEventListener('click', function() {
            sessionStorage.removeItem('currentFileId');
            sessionStorage.removeItem('currentFileName');
            // Use BASE_PATH for redirect (works with subdirectory hosting like GitHub Pages)
            window.location.href = BASE_PATH + 'index.html';
        });
    }
}

function setupExportDropdown() {
    // Toggle dropdown visibility for Export As
    const exportFormatBtn = document.getElementById('exportFormatBtn');
    const exportMenu = document.getElementById('exportMenu');
    
    if (exportFormatBtn && exportMenu) {
        exportFormatBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            exportMenu.classList.toggle('show');
            // Close print menu if open
            const printMenu = document.getElementById('printMenu');
            if (printMenu) printMenu.classList.remove('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!exportFormatBtn.contains(e.target) && !exportMenu.contains(e.target)) {
                exportMenu.classList.remove('show');
            }
        });
    }
    
    // Toggle dropdown visibility for Print Formats
    const printFormatBtn = document.getElementById('printFormatBtn');
    const printMenu = document.getElementById('printMenu');
    
    if (printFormatBtn && printMenu) {
        printFormatBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            printMenu.classList.toggle('show');
            // Close export menu if open
            if (exportMenu) exportMenu.classList.remove('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!printFormatBtn.contains(e.target) && !printMenu.contains(e.target)) {
                printMenu.classList.remove('show');
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
                if (printMenu) printMenu.classList.remove('show');
            }
        });
    });
}

async function downloadInFormat(format) {
    if (!currentFileId) return;
    
    try {
        // Get selected and removed question indices
        const selectedIndices = Array.from(selectedQuestions);
        const removedIndices = Array.from(removedQuestions);
        
        // Build query params
        const params = new URLSearchParams();
        if (selectedIndices.length > 0) {
            params.append('selected', selectedIndices.join(','));
        }
        if (removedIndices.length > 0) {
            params.append('removed', removedIndices.join(','));
        }
        
        const queryString = params.toString();
        const url = API_BASE_URL + '/download/export/' + format + '/' + currentFileId + (queryString ? '?' + queryString : '');
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Export failed');
        }
        
        const blob = await response.blob();
        const formatInfo = EXPORT_FORMATS.find(function(f) { return f.id === format; });
        const ext = formatInfo ? formatInfo.ext : format;
        
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = currentFileId + '.' + ext;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
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

// ==================== Selection & Quiz Functions ====================

// Initialize selection section and handlers
function initSelectionSection() {
    const selectionSection = document.getElementById('selectionSection');
    if (selectionSection) {
        selectionSection.classList.remove('hidden');
    }
    
    // Setup select all button
    const selectAllBtn = document.getElementById('selectAllBtn');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', selectAllQuestions);
    }
    
    // Setup deselect all button
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', deselectAllQuestions);
    }
    
    // Setup generate quiz button
    const generateQuizBtn = document.getElementById('generateQuizBtn');
    if (generateQuizBtn) {
        generateQuizBtn.addEventListener('click', openQuizModal);
    }
    
    // Setup quiz modal
    setupQuizModal();
    
    // Select all by default
    selectAllQuestions();
}

function selectAllQuestions() {
    selectedQuestions.clear();
    const availableMcqs = getAvailableMcqs();
    availableMcqs.forEach(function(mcq, index) {
        selectedQuestions.add(mcq.originalIndex);
    });
    updateSelectionUI();
    updateMcqCardSelections();
}

function deselectAllQuestions() {
    selectedQuestions.clear();
    updateSelectionUI();
    updateMcqCardSelections();
}

function updateSelectionUI() {
    const selectionCount = document.getElementById('selectionCount');
    if (selectionCount) {
        selectionCount.textContent = selectedQuestions.size + ' selected';
    }
}

function getAvailableMcqs() {
    // Return MCQs that are not removed
    return currentMcqs
        .map(function(mcq, index) {
            return { mcq: mcq, originalIndex: index };
        })
        .filter(function(item) {
            return !removedQuestions.has(item.originalIndex);
        });
}

function getSelectedMcqs() {
    // Return MCQs that are selected and not removed
    return currentMcqs
        .map(function(mcq, index) {
            return { mcq: mcq, originalIndex: index };
        })
        .filter(function(item) {
            return selectedQuestions.has(item.originalIndex) && !removedQuestions.has(item.originalIndex);
        })
        .map(function(item) {
            return item.mcq;
        });
}

function setupQuizModal() {
    const modal = document.getElementById('quizModal');
    const modalOverlay = document.getElementById('quizModalOverlay');
    const cancelBtn = document.getElementById('cancelQuizBtn');
    const quizAllBtn = document.getElementById('quizAllBtn');
    const quizRandomBtn = document.getElementById('quizRandomBtn');
    const randomCountSection = document.getElementById('randomCountSection');
    const startQuizBtn = document.getElementById('startQuizBtn');
    const customCountInput = document.getElementById('customQuestionCount');
    const randomCountBtns = document.querySelectorAll('.random-count-btn');
    
    // Cancel button
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeQuizModal);
    }
    
    // Modal overlay click
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeQuizModal);
    }
    
    // Quiz type selection
    if (quizAllBtn) {
        quizAllBtn.addEventListener('click', function() {
            quizType = 'all';
            quizAllBtn.classList.add('selected');
            quizRandomBtn.classList.remove('selected');
            if (randomCountSection) randomCountSection.classList.add('hidden');
            updateStartQuizButton();
        });
    }
    
    if (quizRandomBtn) {
        quizRandomBtn.addEventListener('click', function() {
            quizType = 'random';
            quizRandomBtn.classList.add('selected');
            quizAllBtn.classList.remove('selected');
            if (randomCountSection) randomCountSection.classList.remove('hidden');
            updateStartQuizButton();
        });
    }
    
    // Random count buttons
    randomCountBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            randomCountBtns.forEach(function(b) { b.classList.remove('selected'); });
            btn.classList.add('selected');
            selectedRandomCount = parseInt(btn.getAttribute('data-count'));
            if (customCountInput) customCountInput.value = '';
            updateStartQuizButton();
        });
    });
    
    // Custom count input
    if (customCountInput) {
        customCountInput.addEventListener('input', function() {
            randomCountBtns.forEach(function(b) { b.classList.remove('selected'); });
            selectedRandomCount = parseInt(this.value) || 0;
            updateStartQuizButton();
        });
    }
    
    // Start quiz button
    if (startQuizBtn) {
        startQuizBtn.addEventListener('click', startQuiz);
    }
}

function openQuizModal() {
    const modal = document.getElementById('quizModal');
    const allQuestionsCount = document.getElementById('allQuestionsCount');
    const quizAllBtn = document.getElementById('quizAllBtn');
    const quizRandomBtn = document.getElementById('quizRandomBtn');
    const customCountInput = document.getElementById('customQuestionCount');
    
    // Reset modal state
    quizType = 'all';
    selectedRandomCount = 0;
    
    // Get available (not removed) and selected counts
    const availableCount = getAvailableMcqs().length;
    const selectedCount = selectedQuestions.size;
    
    // For "All Questions" option - show selected count (not removed)
    if (allQuestionsCount) {
        allQuestionsCount.textContent = selectedCount + ' questions selected';
    }
    
    // For random option - use available count
    if (customCountInput) {
        customCountInput.placeholder = 'Custom (max ' + availableCount + ')';
        customCountInput.max = availableCount;
    }
    
    if (quizAllBtn) quizAllBtn.classList.add('selected');
    if (quizRandomBtn) quizRandomBtn.classList.remove('selected');
    
    const randomCountSection = document.getElementById('randomCountSection');
    if (randomCountSection) randomCountSection.classList.add('hidden');
    
    // Clear custom input
    if (customCountInput) customCountInput.value = '';
    
    // Clear button selections
    document.querySelectorAll('.random-count-btn').forEach(function(btn) {
        btn.classList.remove('selected');
    });
    
    updateStartQuizButton();
    
    if (modal) modal.classList.remove('hidden');
}

function closeQuizModal() {
    const modal = document.getElementById('quizModal');
    if (modal) modal.classList.add('hidden');
}

function updateStartQuizButton() {
    const startBtn = document.getElementById('startQuizBtn');
    if (!startBtn) return;
    
    const availableCount = getAvailableMcqs().length;
    let canStart = false;
    
    if (quizType === 'all') {
        canStart = availableCount > 0;
    } else {
        canStart = selectedRandomCount > 0 && selectedRandomCount <= availableCount;
    }
    
    startBtn.disabled = !canStart;
}

function startQuiz(e) {
    if (e) e.preventDefault();
    
    // Get all available questions (selected and not removed)
    let availableQuestions = getSelectedMcqs();
    
    if (availableQuestions.length === 0) {
        showToast('No questions selected for quiz. Please select at least one question.', 'error');
        return;
    }
    
    let quizQuestions = [];
    
    if (quizType === 'all') {
        // Use all selected (not removed) questions
        quizQuestions = availableQuestions;
    } else {
        // Get random questions from selected (not removed)
        const count = Math.min(selectedRandomCount, availableQuestions.length);
        
        // Shuffle and slice
        const shuffled = shuffleArray([...availableQuestions]);
        quizQuestions = shuffled.slice(0, count);
    }
    
    if (quizQuestions.length === 0) {
        showToast('No questions available for quiz', 'error');
        return;
    }
    
    // Store quiz data in sessionStorage
    sessionStorage.setItem('quizQuestions', JSON.stringify(quizQuestions));
    sessionStorage.setItem('quizType', quizType);
    sessionStorage.setItem('selectedRandomCount', selectedRandomCount.toString());
    
    // Use BASE_PATH for redirect (works with subdirectory hosting like GitHub Pages)
    // BASE_PATH is already defined at the top of the file
    window.location.href = BASE_PATH + 'quiz.html';
}

// Fisher-Yates shuffle
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

// Update MCQ card with checkbox and delete button
function updateMcqCardSelections() {
    const cards = document.querySelectorAll('.mcq-card');
    cards.forEach(function(card, index) {
        const checkbox = card.querySelector('.mcq-checkbox');
        if (checkbox) {
            checkbox.checked = selectedQuestions.has(index);
        }
    });
}

function createMcqCard(mcq, number) {
    const card = document.createElement('div');
    card.className = 'mcq-card';
    card.setAttribute('data-index', number - 1);
    
    // Check if removed
    if (removedQuestions.has(number - 1)) {
        card.classList.add('removed');
    }
    
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
    
    card.innerHTML = '<div class="mcq-card-header">' +
        '<div class="mcq-checkbox-wrapper">' +
        '<input type="checkbox" class="mcq-checkbox" id="mcq-check-' + (number - 1) + '" ' + 
        (selectedQuestions.has(number - 1) ? 'checked' : '') + '>' +
        '<label class="mcq-checkbox-label" for="mcq-check-' + (number - 1) + '">Select</label>' +
        '</div>' +
        '<button class="mcq-delete-btn" title="Remove question">' +
        '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">' +
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />' +
        '</svg>' +
        '</button>' +
        '</div>' +
        '<div class="mcq-number">' + number + '</div>' +
        '<div class="mcq-question">' + escapeHtml(mcq.question || '') + '</div>' +
        '<div class="mcq-options">' + optionsHtml + '</div>';
    
    // Add checkbox event listener
    const checkbox = card.querySelector('.mcq-checkbox');
    if (checkbox) {
        checkbox.addEventListener('change', function() {
            const index = parseInt(card.getAttribute('data-index'));
            if (this.checked) {
                selectedQuestions.add(index);
            } else {
                selectedQuestions.delete(index);
            }
            updateSelectionUI();
        });
    }
    
    // Add delete button event listener
    const deleteBtn = card.querySelector('.mcq-delete-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            const index = parseInt(card.getAttribute('data-index'));
            toggleRemoveQuestion(index, card);
        });
    }
    
    return card;
}

function toggleRemoveQuestion(index, card) {
    if (removedQuestions.has(index)) {
        // Restore
        removedQuestions.delete(index);
        card.classList.remove('removed');
        showToast('Question restored', 'success');
    } else {
        // Remove
        removedQuestions.add(index);
        card.classList.add('removed');
        selectedQuestions.delete(index);
        showToast('Question removed', 'success');
    }
    updateSelectionUI();
    
    // Update all questions count display in quiz modal (if open)
    const allQuestionsCount = document.getElementById('allQuestionsCount');
    if (allQuestionsCount) {
        const selectedCount = selectedQuestions.size;
        allQuestionsCount.textContent = selectedCount + ' questions selected';
    }
    
    // Also update the random option max count
    const customCountInput = document.getElementById('customQuestionCount');
    if (customCountInput) {
        const availableCount = getAvailableMcqs().length;
        customCountInput.placeholder = 'Custom (max ' + availableCount + ')';
        customCountInput.max = availableCount;
    }
    
    updateStartQuizButton();
}

// Override displayMcqs to add selection section
const originalDisplayMcqs = displayMcqs;
displayMcqs = function(mcqs) {
    originalDisplayMcqs(mcqs);
    initSelectionSection();
};

window.MCQPreview = { 
    loadMcqs: loadMcqs, 
    displayMcqs: displayMcqs, 
    downloadInFormat: downloadInFormat,
    getSelectedMcqs: getSelectedMcqs,
    getAvailableMcqs: getAvailableMcqs
};
