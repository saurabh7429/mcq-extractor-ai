/**
 * download.js - Handle JSON download functionality
 */

const API_BASE_URL = '/api';

// ==================== Download Functions ====================

/**
 * Download JSON file by file_id
 * @param {string} fileId - The UUID of the file to download
 */
async function downloadJsonById(fileId) {
    try {
        const response = await fetch(`${API_BASE_URL}/download/${fileId}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to download file');
        }
        
        // Get the blob from response
        const blob = await response.blob();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileId}.json`;
        
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        return true;
        
    } catch (error) {
        console.error('Download error:', error);
        throw error;
    }
}

/**
 * Download JSON file directly from URL
 * @param {string} url - The URL to download from
 * @param {string} filename - The filename to save as
 */
async function downloadJsonFromUrl(url, filename = 'mcqs.json') {
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Failed to download file');
        }
        
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(blobUrl);
        document.body.removeChild(a);
        
        return true;
        
    } catch (error) {
        console.error('Download error:', error);
        throw error;
    }
}

/**
 * Get the download URL for a file
 * @param {string} fileId - The UUID of the file
 * @returns {string} The download URL
 */
function getDownloadUrl(fileId) {
    return `${API_BASE_URL}/download/${fileId}`;
}

/**
 * Check if a file exists for download
 * @param {string} fileId - The UUID of the file
 * @returns {Promise<boolean>} True if file exists
 */
async function checkFileExists(fileId) {
    try {
        const response = await fetch(`${API_BASE_URL}/download/${fileId}`, {
            method: 'HEAD'
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

/**
 * List all available files for download
 * @returns {Promise<Object>} Object with json_files and pdf_files arrays
 */
async function listAvailableFiles() {
    try {
        const response = await fetch(`${API_BASE_URL}/download/list`);
        
        if (!response.ok) {
            throw new Error('Failed to list files');
        }
        
        const data = await response.json();
        return data.data;
        
    } catch (error) {
        console.error('List files error:', error);
        throw error;
    }
}

// Export for use in other modules
window.MCQDownload = {
    downloadJsonById,
    downloadJsonFromUrl,
    getDownloadUrl,
    checkFileExists,
    listAvailableFiles
};
