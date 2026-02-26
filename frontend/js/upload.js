/**
 * upload.js - Handle file upload functionality
 */

// Get API URL from config - set your backend URL in config.js
// For production: change API_BASE_URL in config.js to your Render backend URL
const API_BASE_URL = typeof API !== 'undefined' ? API : '/api';

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

    // Validate file size (10MB = 10 * 1024 * 1024 bytes)
    if (!validateFileSize(file)) {
        showError('File too large. Maximum size is 10MB.', 'Please compress your PDF or use a smaller file.');
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
    const maxSize = 10 * 1024 * 1024; // 10MB
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
        try {
            uploadData = uploadText ? JSON.parse(uploadText) : null;
        } catch (e) {
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

        // Extract MCQs
        showLoading('Extracting MCQs...', 'Using AI to analyze and extract questions');

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
                // Try to generate suggestion from error
                suggestion = extractData.suggestion || _generateSuggestion(extractData.error);
            } else if (!extractResponse.ok) {
                suggestion = 'Please check if the server is running and try again.';
            }
            const msg = (extractData && extractData.error) ? extractData.error : 'Extraction failed (invalid server response)';
            throw new Error(msg);
        }

        // Update status - Saving to database
        showLoading('Saving to database...', 'Storing your MCQs securely');

        // Store file_id in sessionStorage for preview page
        sessionStorage.setItem('currentFileId', fileId);
        sessionStorage.setItem('currentFileName', selectedFile.name);

        // Hide loading
        hideLoading();

        // Show success message
        showSuccess();

        // Redirect to preview page after short delay
        setTimeout(() => {
            window.location.href = 'preview.html';
        }, 1500);

    } catch (error) {
        console.error('Upload error:', error);
        hideLoading();
        
        // Try to extract suggestion from error
        let suggestion = null;
        if (error.message) {
            suggestion = _generateSuggestion(error.message);
        }
        
        showError(error.message || 'An error occurred during upload. Please try again.', suggestion);
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

// Export for use in other modules
window.MCQUploader = {
    removeFile,
    uploadFile
};
