/**
 * upload.js - Handle file upload functionality
 */

// Dynamic API_BASE_URL based on deployment
// Local development: http://localhost:5000/api
// GitHub Pages: https://saurabh7429.github.io/mcq-extractor-ai/
// Render: https://mcq-extractor-ai.onrender.com/api
const API_BASE_URL = (function() {
    const hostname = window.location.hostname;
    // Localhost or 127.0.0.1
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return '/api';
    }
    // GitHub Pages - use Render API (since it's a static site)
    if (hostname.includes('github.io')) {
        return 'https://mcq-extractor-ai.onrender.com/api';
    }
    // Render - same origin
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
    // Check if the second part looks like a repo name (not a file like preview.html or index.html)
    // Repo names typically don't have dots and are not .html files
    if (parts.length > 1 && parts[1] && !parts[1].endsWith('.html') && parts[1] !== '') {
        return '/' + parts[1] + '/';
    }
    return '/';
})();

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const selectedFileDiv = document.getElementById('selectedFile');
const fileNameEl = document.getElementById('fileName');
const fileSizeEl = document.getElementById('fileSize');
const removeFileBtn = document.getElementById('removeFile');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const errorSuggestion = document.getElementById('errorSuggestion');

// State
let selectedFile = null;

// ==================== Event Listeners ====================

// Drop zone click
dropZone.addEventListener('click', () => fileInput.click());

// File input change
fileInput.addEventListener('change', handleFileSelect);

// Drag and drop events
dropZone.addEventListener('dragover', handleDragOver);
dropZone.addEventListener('dragleave', handleDragLeave);
dropZone.addEventListener('drop', handleDrop);

// Remove file button
removeFileBtn.addEventListener('click', removeFile);

// Upload button
uploadBtn.addEventListener('click', uploadFile);

// ==================== File Handling ====================

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    dropZone.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    dropZone.classList.remove('drag-over');

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        processFile(file);
    }
}

function processFile(file) {
    // Clear previous error
    hideError();

    // Validate file type
    if (!validateFileType(file)) {
        showError('Invalid file type. Please upload a PDF file.', 'Only PDF files (.pdf) are allowed.');
        return;
    }

    // Validate file size (20MB = 20 * 1024 * 1024 bytes)
    if (!validateFileSize(file)) {
        showError('File too large. Maximum size is 20MB.', 'Please compress your PDF or use a smaller file.');
        return;
    }

    selectedFile = file;
    displaySelectedFile(file);
    enableUploadButton();
}

function validateFileType(file) {
    const allowedTypes = ['application/pdf'];
    const allowedExtensions = ['.pdf'];
    
    // Check MIME type
    if (allowedTypes.includes(file.type)) {
        return true;
    }
    
    // Check extension
    const fileName = file.name.toLowerCase();
    return allowedExtensions.some(ext => fileName.endsWith(ext));
}

function validateFileSize(file) {
    const maxSize = 20 * 1024 * 1024; // 20MB
    return file.size <= maxSize;
}

function displaySelectedFile(file) {
    fileNameEl.textContent = file.name;
    fileSizeEl.textContent = formatFileSize(file.size);
    selectedFileDiv.classList.remove('hidden');
    dropZone.classList.add('hidden');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function removeFile() {
    selectedFile = null;
    fileInput.value = '';
    selectedFileDiv.classList.add('hidden');
    dropZone.classList.remove('hidden');
    disableUploadButton();
    hideError();
}

function enableUploadButton() {
    uploadBtn.disabled = false;
}

function disableUploadButton() {
    uploadBtn.disabled = true;
}

// ==================== Error Handling ====================

function showError(message, suggestion = null) {
    errorText.textContent = message;
    
    // Show suggestion if available
    if (suggestion && errorSuggestion) {
        errorSuggestion.textContent = suggestion;
        errorSuggestion.classList.remove('hidden');
    } else if (errorSuggestion) {
        errorSuggestion.classList.add('hidden');
    }
    
    errorMessage.classList.remove('hidden');
    // Auto-hide after 8 seconds for longer reading time
    setTimeout(hideError, 8000);
}

function hideError() {
    errorMessage.classList.add('hidden');
}

// ==================== File Upload ====================

// Polling interval for checking job status
let jobPollingInterval = null;
const JOB_POLL_INTERVAL = 2000; // Check every 2 seconds

async function uploadFile() {
    if (!selectedFile) {
        showError('Please select a file first.', 'Click on the drop zone or drag and drop a PDF file.');
        return;
    }

    try {
        // Show loading state
        showLoading('Uploading PDF...', 'Please wait while we upload your file');

        // Create form data
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Upload file
        const uploadResponse = await fetch(`${API_BASE_URL}/upload/file`, {
            method: 'POST',
            body: formData
        });

        let uploadData = null;
        let uploadText = await uploadResponse.text();
        
        // Debug: Log the response
        console.log('Upload response status:', uploadResponse.status);
        console.log('Upload response text:', uploadText.substring(0, 500));
        
        try {
            uploadData = uploadText ? JSON.parse(uploadText) : null;
        } catch (e) {
            console.error('Failed to parse upload response:', e);
            // If response is HTML (error page), show more helpful message
            if (uploadText.includes('<!DOCTYPE') || uploadText.includes('<html')) {
                throw new Error('API server error. Please check if the server is running properly.');
            }
            uploadData = null;
        }

        if (!uploadResponse.ok || !uploadData) {
            // Try to get suggestion from response
            let suggestion = null;
            if (uploadData && uploadData.suggestion) {
                suggestion = uploadData.suggestion;
            } else if (!uploadResponse.ok) {
                suggestion = 'Please check if the server is running and try again.';
            }
            const msg = (uploadData && uploadData.message) ? uploadData.message : 'Upload failed (invalid server response)';
            throw new Error(msg);
        }

        const fileId = uploadData.file_id;

        // Update status - Reading PDF
        showLoading('Reading PDF...', 'Extracting text from your PDF document');

        // Extract MCQs - start background job
        showLoading('Starting extraction...', 'Your PDF is being processed');

        const extractResponse = await fetch(`${API_BASE_URL}/extract/${fileId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        let extractData = null;
        let extractText = await extractResponse.text();
        try {
            extractData = extractText ? JSON.parse(extractText) : null;
        } catch (e) {
            extractData = null;
        }

        if (!extractResponse.ok || !extractData) {
            // Get suggestion from response if available
            let suggestion = null;
            if (extractData && extractData.suggestion) {
                suggestion = extractData.suggestion;
            } else if (extractData && extractData.error) {
                suggestion = extractData.suggestion || _generateSuggestion(extractData.error);
            } else if (!extractResponse.ok) {
                suggestion = 'Please check if the server is running and try again.';
            }
            const msg = (extractData && extractData.error) ? extractData.error : 'Extraction failed (invalid server response)';
            throw new Error(msg);
        }

        // Check if we got a job_id (background processing) or immediate result
        if (extractData.job_id) {
            // Background job - poll for status
            const jobId = extractData.job_id;
            console.log('Job started with ID:', jobId);
            
            // Store job_id and file_id for status polling
            sessionStorage.setItem('currentJobId', jobId);
            sessionStorage.setItem('currentFileId', fileId);
            sessionStorage.setItem('currentFileName', selectedFile.name);
            
            // Start polling for job status
            await pollJobStatus(jobId, fileId);
        } else if (extractData.cached) {
            // Cached result - go directly to preview
            sessionStorage.setItem('currentFileId', fileId);
            sessionStorage.setItem('currentFileName', selectedFile.name);
            hideLoading();
            showSuccess();
            setTimeout(() => {
                window.location.href = BASE_PATH + 'preview.html';
            }, 1500);
        } else {
            // Immediate result (shouldn't happen with new implementation)
            sessionStorage.setItem('currentFileId', fileId);
            sessionStorage.setItem('currentFileName', selectedFile.name);
            hideLoading();
            showSuccess();
            setTimeout(() => {
                window.location.href = BASE_PATH + 'preview.html';
            }, 1500);
        }

    } catch (error) {
        console.error('Upload error:', error);
        hideLoading();
        
        // Stop polling if active
        stopJobPolling();
        
        // Try to extract suggestion from error
        let suggestion = null;
        if (error.message) {
            suggestion = _generateSuggestion(error.message);
        }
        
        showError(error.message || 'An error occurred during upload. Please try again.', suggestion);
    }
}

async function pollJobStatus(jobId, fileId) {
    // Show initial loading state
    showLoading('Processing your PDF...', 'This may take a few moments');
    
    return new Promise((resolve, reject) => {
        jobPollingInterval = setInterval(async () => {
            try {
                const statusResponse = await fetch(`${API_BASE_URL}/status/${jobId}`);
                
                if (!statusResponse.ok) {
                    console.error('Status check failed:', statusResponse.status);
                    return;
                }
                
                const statusData = await statusResponse.json();
                console.log('Job status:', statusData);
                
                if (!statusData.success) {
                    console.error('Job status error:', statusData);
                    return;
                }
                
                // Update loading UI with progress
                updateLoadingProgress(statusData);
                
                // Check if completed
                if (statusData.status === 'completed') {
                    stopJobPolling();
                    
                    // Store file_id for preview
                    sessionStorage.setItem('currentFileId', fileId);
                    sessionStorage.setItem('currentFileName', selectedFile.name);
                    
                    hideLoading();
                    showSuccess();
                    
                    // Redirect to preview page
                    setTimeout(() => {
                        window.location.href = BASE_PATH + 'preview.html';
                    }, 1500);
                    
                    resolve(statusData);
                }
                
                // Check if failed
                if (statusData.status === 'failed') {
                    stopJobPolling();
                    hideLoading();
                    
                    let errorMsg = statusData.error || 'Extraction failed';
                    showError(errorMsg, _generateSuggestion(errorMsg));
                    
                    reject(new Error(errorMsg));
                }
                
            } catch (error) {
                console.error('Error polling job status:', error);
            }
        }, JOB_POLL_INTERVAL);
    });
}

function stopJobPolling() {
    if (jobPollingInterval) {
        clearInterval(jobPollingInterval);
        jobPollingInterval = null;
    }
}

function updateLoadingProgress(statusData) {
    const loadingTitle = document.getElementById('loadingTitle');
    const loadingSubtitle = document.getElementById('loadingSubtitle');
    const progressBar = document.getElementById('progressBar');
    
    // Map stages to user-friendly messages
    const stageMessages = {
        'reading_pdf': 'Reading PDF...',
        'extracting_text': 'Extracting text...',
        'ai_processing': 'Analyzing with AI...',
        'formatting': 'Formatting MCQs...',
        'saving': 'Saving results...',
        'completed': 'Complete!'
    };
    
    const stage = statusData.stage || 'processing';
    const progress = statusData.progress || 0;
    const message = statusData.message || stageMessages[stage] || 'Processing...';
    
    // Update UI
    if (loadingTitle) {
        loadingTitle.textContent = stageMessages[stage] || 'Processing...';
    }
    if (loadingSubtitle) {
        let subtitle = message;
        // Add additional info if available
        if (statusData.mcqs_found !== undefined) {
            subtitle += ` (${statusData.mcqs_found} MCQs found)`;
        }
        if (statusData.pages_processed && statusData.total_pages) {
            subtitle += ` - Page ${statusData.pages_processed}/${statusData.total_pages}`;
        }
        loadingSubtitle.textContent = subtitle;
    }
    if (progressBar) {
        progressBar.style.width = `${Math.min(progress, 100)}%`;
    }
}

// Helper function to generate suggestions based on error message
function _generateSuggestion(errorMsg) {
    const msg = errorMsg.toLowerCase();
    
    if (msg.includes('no text found') || msg.includes('scanned') || msg.includes('image-based')) {
        return 'Try using a text-based PDF or install OCR: pip install pytesseract pdf2image';
    } else if (msg.includes('pdf') && (msg.includes('not found') || msg.includes('invalid'))) {
        return 'Please upload a valid PDF file. The file may be corrupted.';
    } else if (msg.includes('api') && msg.includes('key')) {
        return 'Check your GEMINI_API_KEY in the .env file.';
    } else if (msg.includes('database') || msg.includes('db')) {
        return 'Please restart the server to initialize the database.';
    } else if (msg.includes('connection') || msg.includes('network')) {
        return 'Please check your internet connection and try again.';
    } else if (msg.includes('quota') || msg.includes('rate limit')) {
        return 'API quota exceeded. Please try again later.';
    }
    
    return 'Please try again or contact support if the problem persists.';
}

// ==================== Loading States ====================

function showLoading(title, subtitle) {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const loadingTitle = document.getElementById('loadingTitle');
    const loadingSubtitle = document.getElementById('loadingSubtitle');
    const progressBar = document.getElementById('progressBar');
    
    loadingTitle.textContent = title;
    loadingSubtitle.textContent = subtitle;
    progressBar.style.width = '0%';
    
    loadingSpinner.classList.remove('hidden');
    
    // Animate progress bar
    animateProgressBar();
}

function hideLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    loadingSpinner.classList.add('hidden');
}

function animateProgressBar() {
    const progressBar = document.getElementById('progressBar');
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

function showSuccess() {
    const successMessage = document.getElementById('successMessage');
    successMessage.classList.remove('hidden');
}

