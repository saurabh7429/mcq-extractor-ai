# Changelog - MCQ Extractor AI

All notable changes to this project will be documented in this file.

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
