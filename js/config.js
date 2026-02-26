/**
 * Configuration file for MCQ Extractor AI
 * Set up your backend API URL here
 */

const Config = {
    // Backend API URL - Update this to your Render backend URL
    API_BASE_URL: 'https://mcq-extractor-backend.onrender.com',
    
    // API Endpoints
    API_ENDPOINTS: {
        UPLOAD: '/api/upload/file',
        VALIDATE: '/api/upload/validate',
        EXTRACT: '/api/extract/process',
        PREVIEW: '/api/extract/preview',
        DOWNLOAD_JSON: '/api/download/json',
        DOWNLOAD_PDF: '/api/download/pdf'
    },
    
    // Get full URL for an endpoint
    getUrl: function(endpoint) {
        return this.API_BASE_URL + endpoint;
    }
};

// Make it globally available
window.API_BASE_URL = Config.API_BASE_URL;
window.API_ENDPOINTS = Config.API_ENDPOINTS;
window.getApiUrl = Config.getUrl.bind(Config);

console.log('API Configuration loaded:', Config.API_BASE_URL);
