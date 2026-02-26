/**
 * upload.js - Handle file upload functionality
 */

// Get API URL from config
const API_BASE_URL = window.API_BASE_URL || '';

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
        showError('Invalid file type. Please upload a PDF file.');
        return;
    }

    // Validate file size (10MB = 10 * 1024 * 1024 bytes)
    if (!validateFileSize(file)) {
        showError('File too large. Maximum size is 10MB.');
        return;
    }

    selectedFile = file;
    displaySelectedFile(file);
    enableUploadButton();
}

function validateFileType(file) {
    const allowedTypes = ['application/pdf'];
    return allowedTypes.includes(file.type);
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
    uploadBtn.removeAttribute('disabled');
}

function disableUploadButton() {
    uploadBtn.setAttribute('disabled', 'true');
}

// ==================== Upload Function ====================

async function uploadFile() {
    if (!selectedFile) {
        showError('Please select a file first.');
        return;
    }

    // Clear previous errors
    hideError();

    try {
        // Show loading state
        showLoading('Uploading PDF...', 'Please wait while your file is being uploaded');

        // Create FormData
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Upload file
        const uploadResponse = await fetch(API_BASE_URL + '/api/upload/file', {
            method: 'POST',
            body: formData
        });

        const uploadData = await uploadResponse.json();

        if (!uploadResponse.ok || uploadData.status === 'error') {
            const msg = uploadData.message || 'Upload failed';
            throw new Error(msg);
        }

        const fileId = uploadData.file_id;

        // Update status - Extracting MCQs
        showLoading('Extracting MCQs...', 'AI is analyzing your PDF');

        // Extract MCQs
        const extractResponse = await fetch(API_BASE_URL + '/api/extract/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_id: fileId })
        });

        const extractData = await extractResponse.json();

        if (!extractResponse.ok || !extractData) {
            const msg = (extractData && extractData.message) ? extractData.message : 'Extraction failed';
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
        showError(error.message || 'An error occurred during upload. Please try again.');
    }
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

// ==================== Error Handling ====================

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

// Export for use in other modules
window.MCQUploader = {
    removeFile,
    uploadFile
};
