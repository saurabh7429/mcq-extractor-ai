# Changelog - MCQ Extractor AI

All notable changes to this project will be documented in this file.

---

## [Version 2.0.0] - 2025-02-26

### Changed
- **API Switch**: Migrated from Google Gemini to GROQ API for MCQ extraction
- **Model Selection**: 
  - Production: `llama-3.3-70b-versatile` (Llama 3.3 70B)
  - Testing: `llama-3.1-8b-instant` (Llama 3.1 8B)
- **Environment-based Model**: Automatically selects model based on `FLASK_ENV`
- **Updated Dependencies**: Added `groq>=0.4.0` to requirements.txt

### Updated Files
- `.env.example`: Added GROQ_API_KEY configuration
- `backend/config.py`: Added GROQ_API_KEY support
- `backend/services/ai_processor.py`: Replaced Gemini with GROQ API
- `backend/utils/error_handler.py`: Updated API key error suggestions
- `frontend/index.html`: Added version and last update display
- `frontend/css/styles.css`: Added version info styling
- `tests/test_ai_processor.py`: Updated test expectations

### Testing Files
- `testmcq.pdf`: Contains 11 MCQ questions for testing
- `testmcq2.pdf`: Contains 173 MCQ questions for testing

### How to Use
1. Get GROQ API key from https://console.groq.com/keys
2. Add to `.env` file: `GROQ_API_KEY=your-api-key`
3. Run production: `python run.py` (uses Llama 3.3 70B)
4. Run testing: `FLASK_ENV=testing python run.py` (uses Llama 3.1 8B)

---

## [Version 1.1.1] - 2025-02-25

### Added
- **Improved Error Messages**: Added detailed, user-friendly error messages throughout the application
- **Error Suggestions**: Each error now includes helpful suggestions to help users resolve issues
- **Backend Error Handling**: Enhanced error_handler.py with context-aware suggestions for:
  - Scanned PDF errors (OCR installation instructions)
  - API key errors (GEMINI_API_KEY setup)
  - Database errors (restart instructions)
  - Network/connection errors
  - File size/memory errors

### Changed
- **PDF Reader** (pdf_reader.py): 
  - Added custom exceptions PDFReadError and PDFNoTextError
  - Added detailed error messages with installation instructions for OCR
  - Better handling of different PDF types
  
- **Extract Route** (extract.py):
  - Added specific error handling for PDFReadError and PDFNoTextError
  - Better error propagation to frontend
  
- **Frontend Upload** (upload.js):
  - Added error suggestion display with helpful tips
  - Better parsing of server error responses
  - Extended auto-hide time for error messages (8 seconds)

- **Requirements** (requirements.txt):
  - Updated to latest versions of all packages
  - PyPDF2 replaced with pypdf (more actively maintained)
  - All packages now use latest stable versions

### Fixed
- **Upload Error - "invalid server response"**: 
  - Previously, when server returned errors, users got generic "invalid server response" message
  - Now server returns proper JSON with error details and suggestions
  - Frontend displays both error message AND helpful suggestion

---

## [Version 1.1.0] - 2025-02-25

### Added
- **OCR Support for Scanned PDFs**: Added automatic OCR (Optical Character Recognition) support for scanned/image-based PDFs using pytesseract and pdf2image
- When a PDF has no extractable text, the system automatically tries to extract text using OCR
- New dependencies added: `pytesseract>=0.3.10`, `pdf2image`

### Fixed
- **Preview Page Error**: Fixed "Unexpected token '<', "<!DOCTYPE "... is not valid JSON" error
  - Backend endpoint `/api/extract/<file_id>` now supports both GET and POST methods (was only POST before)
  - Frontend was making GET request but backend only accepted POST

### Changed
- Updated requirements.txt with OCR dependencies

---

## [Version 1.0.0] - 2025-02-24

### Added
- Initial release
- PDF upload functionality
- MCQ extraction using AI (Gemini)
- Preview extracted MCQs
- Download MCQs as JSON

---

## Previous Issues Resolved

### Upload Error - "Upload failed (invalid server response)"
- **Cause**: Server was not running
- **Solution**: Start server with `python run.py`

### Upload Error - "Upload failed (invalid server response)" (after server started)
- **Cause**: Server returned HTML error page instead of JSON
- **Solution**: Ensure server is running and accessible at http://localhost:5000

### Preview Page Error - "Unexpected token '<', "<!DOCTYPE "... is not valid JSON"
- **Cause**: Backend endpoint only accepted POST, frontend was making GET
- **Solution**: Added GET method support to `/api/extract/<file_id>` endpoint

### PDF Text Extraction Error - "No text found in PDF. The PDF may be scanned or image-based."
- **Cause**: Uploaded PDFs were scanned/image-based with no text layer
- **Solution**: Added OCR support to automatically extract text from scanned PDFs

---

## Installation for OCR Support

To use OCR functionality, you need to install additional dependencies:

```
bash
# Install Python dependencies
pip install -r requirements.txt

# Install Tesseract OCR (system dependency)
# Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

---

## Notes

- Text-based PDFs work without OCR (faster)
- OCR is only triggered when no text is found in PDF (automatic fallback)
- OCR may take longer for large documents
