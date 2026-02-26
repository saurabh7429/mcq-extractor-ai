# Update Details - MCQ Extractor AI

## Update History

---

### Update 003 - 2025-02-25
**Type**: Major UI Update (Major Update: 1.x.x → 2.0.0)

#### New Features:
1. **Logo Addition**
   - Added site logo (logo.png) to header on both index.html and preview.html
   - Logo displays with hover animation effect

2. **Enhanced Drag & Drop Area**
   - Made drop zone bigger and more prominent for PC users
   - Added enhanced mobile-optimized drop zone design
   - Better visual feedback during drag-over with smooth animations
   - Larger touch targets for mobile devices

3. **Improved UI & Animations**
   - Added sophisticated entrance animations with staggered delays
   - Improved color scheme with professional gradients
   - Added smooth hover effects with transitions throughout
   - Added floating background particles effect
   - Added shimmer effect on progress bar
   - Enhanced card hover effects with colored top border

4. **Preview Page - Correct Answer Highlighting**
   - Modified preview.js to properly identify correct answers
   - Correct answer now highlighted with green color styling
   - Added "✓ Correct" badge next to correct answer
   - Green pulsing animation for correct answer highlight
   - Better answer detection (supports both letter A/B/C/D and full text)

5. **Mobile Optimization**
   - Better responsive design with larger touch targets
   - Touch-friendly interactions
   - Stable, professional mobile UI
   - Optimized spacing and sizing for all screen sizes

#### Files Modified:
| File | Change Type | Description |
|------|-------------|-------------|
| `frontend/index.html` | Modified | Added logo container and header |
| `frontend/preview.html` | Modified | Added logo container to header |
| `frontend/css/styles.css` | Modified | Complete UI overhaul with animations, mobile styles |
| `frontend/js/preview.js` | Modified | Improved correct answer detection and highlighting |
| `UPDATE.md` | Modified | Added version 2.0.0 changelog |

#### Version: 1.x.x → 2.0.0 (Major Update)

---

### Update 002 - 2025-02-25
**Type**: User Experience Improvement (Minor Update: 1.1.0 → 1.1.1)

#### Issues Fixed:
1. **Generic Error Messages** - Users couldn't understand what went wrong
   - Error: "Upload failed (invalid server response)" - too generic
   - Cause: Backend returned errors without helpful details
   - Fix: Added detailed error messages with suggestions in error_handler.py

2. **Missing OCR Installation Guidance** - Users didn't know how to fix OCR errors
   - Error: "No text found in PDF" without solution
   - Cause: Error message didn't include installation instructions
   - Fix: Added specific OCR installation steps in error messages

3. **Frontend Error Display** - Suggestions weren't shown to users
   - Issue: Only error message was displayed, no helpful tips
   - Fix: Added suggestion element in HTML and proper display in JavaScript

4. **Outdated Dependencies** - Old package versions
   - Issue: PyPDF2 outdated, some packages not at latest versions
   - Fix: Updated requirements.txt with latest stable versions

#### Changes Made:

| File | Change Type | Description |
|------|-------------|-------------|
| `backend/utils/error_handler.py` | Modified | Added suggestions to all error responses |
| `backend/services/pdf_reader.py` | Modified | Added custom exceptions with detailed messages |
| `backend/routes/extract.py` | Modified | Added specific error handling for PDF errors |
| `frontend/js/upload.js` | Modified | Added suggestion display and parsing |
| `frontend/index.html` | Modified | Added suggestion element in error message div |
| `frontend/css/styles.css` | Modified | Added CSS for error suggestion display |
| `requirements.txt` | Modified | Updated all packages to latest versions |
| `CHANGELOG.md` | Modified | Updated with version 1.1.1 details |

#### Updated Dependencies (requirements.txt):

| Package | Old Version | New Version |
|---------|-------------|-------------|
| Flask | >=3.0.0 | >=3.1.0 |
| Flask-CORS | >=4.0.0 | >=5.0.0 |
| Werkzeug | >=3.0.0 | >=3.1.0 |
| python-dotenv | >=1.0.0 | >=1.0.1 |
| SQLAlchemy | >=2.0.36 | >=2.0.36 |
| PyPDF2 | >=3.0.0 | REMOVED |
| pypdf | NEW | >=5.1.0 |
| pdfplumber | >=0.10.0 | >=0.11.0 |
| google-generativeai | >=0.5.0 | >=0.8.0 |
| python-json-logger | >=2.0.0 | >=2.0.7 |
| gunicorn | >=21.0.0 | >=23.0.0 |
| Pillow | >=10.0.0 | >=11.0.0 |
| requests | >=2.31.0 | >=2.32.0 |
| pytesseract | >=0.3.10 | >=0.3.10 |
| pdf2image | >=1.16.0 | >=1.17.0 |

#### Technical Details:

**Backend Error Handler Improvements:**
- Added `_get_suggestion()` method in APIError class
- Each error now includes context-aware suggestions
- Added `details` field for debugging in generic errors
- HTTP status code specific suggestions (400, 401, 403, 404, etc.)

**Frontend Improvements:**
- Error message now auto-hides after 8 seconds (was 5)
- Added `_generateSuggestion()` helper function
- Parses server response for suggestion field
- Shows suggestion below error message in styled element

#### Error Messages Now Include:

| Error Type | Suggestion |
|------------|------------|
| Scanned PDF | "Try using a text-based PDF or install OCR: pip install pytesseract pdf2image" |
| Invalid PDF | "Please upload a valid PDF file. The file may be corrupted." |
| API Key Error | "Check your GEMINI_API_KEY in the .env file." |
| Database Error | "Please restart the server to initialize the database." |
| Network Error | "Please check your internet connection and try again." |
| Server Error | "Please try again or contact support if the problem persists." |

---

### Update 001 - 2025-02-25
**Type**: Feature Addition + Bug Fix (Major Update: 1.0.0 → 1.1.0)

#### Issues Fixed:
1. **Preview Page Error** - JSON loading failure
   - Error: "Unexpected token '<', "<!DOCTYPE "... is not valid JSON"
   - Cause: Backend only accepted POST, frontend sent GET request
   - Fix: Added GET method support to `/api/extract/<file_id>` endpoint

2. **PDF Text Extraction Error** - No text found in scanned PDFs
   - Error: "No text found in PDF. The PDF may be scanned or image-based."
   - Cause: PDF was scanned/image-based with no text layer
   - Fix: Added OCR support using pytesseract and pdf2image

#### New Features:
- **OCR Support**: Automatic text extraction from scanned/image-based PDFs
- Automatic fallback: If no text found, OCR is triggered automatically
- Works with both file path and file object inputs

#### Files Modified:
| File | Change Type | Description |
|------|-------------|------------|
| `backend/routes/extract.py` | Modified | Added GET method support |
| `backend/services/pdf_reader.py` | Modified | Added OCR methods |
| `requirements.txt` | Modified | Added pytesseract dependency |
| `CHANGELOG.md` | Created | Update history documentation |

#### New Dependencies:
- `pytesseract>=0.3.10` - Python OCR library
- `pdf2image` - Convert PDF to images for OCR

#### System Dependencies Required:
- **Windows**: Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

---

### Update 000 - 2025-02-24
**Type**: Initial Release (Version 1.0.0)

#### Initial Features:
- PDF upload functionality
- MCQ extraction using AI (Gemini)
- Preview extracted MCQs
- Download MCQs as JSON

---

## Installation Commands

```
bash
# Install Python dependencies
pip install -r requirements.txt

# Install Tesseract OCR (if not already installed)
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

# Restart server
python run.py
```

---

## Testing Error Messages

To test improved error messages:
1. **Upload without file**: Shows "Please select a file first"
2. **Upload invalid file type**: Shows "Only PDF files (.pdf) are allowed"
3. **Upload file > 10MB**: Shows "File too large" with suggestion
4. **Server not running**: Shows "Please check if the server is running"
5. **Scanned PDF (no OCR)**: Shows OCR installation instructions

---

## Rollback Instructions

If error messages cause issues:
1. No rollback needed - changes are backward compatible
2. Simply revert to previous version of modified files if needed

---

## Next Updates (Planned)

- [ ] Add progress indicator for OCR processing
- [ ] Support for multiple languages in OCR
- [ ] Optimize OCR for better performance
- [ ] Add multi-file upload support
- [ ] Add PDF password protection support
