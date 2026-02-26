/**
 * download.js - Handle download functionality
 */

// Get API URL from config
const API_BASE_URL = window.API_BASE_URL || '';

// ==================== Download PDF ====================
async function downloadPdf() {
    const fileId = sessionStorage.getItem('currentFileId');
    if (!fileId) {
        showToast('No file found', 'error');
        return;
    }

    try {
        const response = await fetch(API_BASE_URL + '/api/download/pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_id: fileId })
        });

        if (!response.ok) {
            throw new Error('Failed to download PDF');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'original-file.pdf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast('PDF downloaded successfully!', 'success');
    } catch (error) {
        console.error('Error downloading PDF:', error);
        showToast('Failed to download PDF', 'error');
    }
}

// ==================== Toast Helper ====================
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

// Export globally
window.downloadPdf = downloadPdf;
window.showToast = showToast;
