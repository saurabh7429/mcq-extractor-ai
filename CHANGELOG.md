# Changelog - MCQ Extractor AI

All notable changes to this project will be documented in this file.

---

## [Version 2.6.1] - 2026-03-08

### Fix - GitHub Pages Like/Dislike System

#### Problem
- Like/Dislike system worked on Render deployment but NOT on GitHub Pages
- GitHub Pages is static hosting and cannot run backend APIs
- API calls used relative paths like `/api/stats` which don't exist on GitHub Pages

#### Solution - Centralized API Base URL
- Created centralized `API_BASE` constant in stats.js
- Detects hosting environment and routes API calls accordingly:
  - **Local development (localhost/127.0.0.1)**: Uses relative paths `/api/stats`
  - **GitHub Pages**: Uses Render backend `https://mcq-extractor-ai.onrender.com/api/stats`
  - **Render deployment**: Uses relative paths `/api/stats`

#### Files Modified
- `js/stats.js` - Added centralized API_BASE with environment detection

#### Benefits
- Works seamlessly on both GitHub Pages (frontend only) and Render (full stack)
- No backend changes required
- Consistent with existing pattern in upload.js and preview.js
- Lightweight implementation suitable for Render free tier (512MB RAM)

---

## [Version 2.6.0] - 2026-03-08

### New Features - Quiz Completion Messages

#### 1. Enhanced Quiz Result Messages
- Expanded from 6 to 26+ unique compliment messages
- Messages are randomly selected for variety
- Messages categorized by score range:

| Score Range | Messages Count | Example Messages |
|-------------|---------------|------------------|
| 90-100% (Excellent) | 6 | "Perfect Score!", "Outstanding!", "Marvelous!", "Phenomenal!" |
| 80-89% (Great) | 5 | "Awesome!", "Superb!", "Impressive!", "Terrific!" |
| 70-79% (Good) | 5 | "Well Done!", "Nice Work!", "Great Effort!", "Thumbs Up!" |
| 60-69% (Not Bad) | 5 | "Decent Job!", "Nice Try!", "Keep Going!" |
| 50-59% (Fair) | 5 | "Almost There!", "Good Start!", "Keep Trying!" |
| Below 50% | 6 | "Don't Give Up!", "Stay Positive!", "You Can Do It!" |

#### 2. Random Message Selection
- Each quiz completion randomly selects a message from the appropriate category
- Adds variety and engagement to the quiz experience
- Encourages users to try again for better scores

### Files Modified
- `js/quiz.js` - Added message arrays with 26+ unique compliments

### Notes
- No backend changes required
- Lightweight implementation - no additional dependencies
- Compatible with existing quiz system

---

## [Version 2.5.0] - 2026-03-08

### New Features - Statistics & Social Links

#### 1. Server Statistics System
- JSON file-based storage (lightweight, no database required)
- View counter: Increments automatically on every PDF extraction
- Like/Dislike system with REST API endpoints:
  - GET /api/stats - Get current statistics
  - POST /api/stats/like - Increment likes
  - POST /api/stats/dislike - Increment dislikes
  - POST /api/stats/view - Manual view increment (also auto-called on extraction)
- Initial values: Views=100, Likes=20, Dislikes=0

#### 2. Anti-Spam System
- Browser localStorage-based protection
- Prevents multiple likes/dislikes from same browser session
- Buttons disabled after voting with visual feedback

#### 3. Social Links (All Pages)
- GitHub: https://github.com/saurabh7429/mcq-extractor-ai
- Instagram: https://www.instagram.com/sa_urabh7429
- Telegram Support Group: https://t.me/+WvSRZuYAoh0yZTg1
- Mobile responsive footer layout

#### 4. Frontend Statistics Display
- Views, Likes, Dislikes displayed with icons
- Like/Dislike buttons with anti-spam protection
- Real-time updates after voting

### Files Added
- `js/stats.js` - Statistics manager with API calls and anti-spam

### Files Modified
- `backend/routes/stats.py` - Added increment_view() function for extraction hook
- `backend/routes/extract.py` - View increment on every extraction
- `storage/stats.json` - JSON storage for statistics
- `css/styles.css` - Statistics section and social links CSS
- `index.html` - Added stats section and social links
- `preview.html` - Added stats section and social links
- `quiz.html` - Added stats section and social links

### Performance
- Lightweight JSON file storage (no database required)
- Minimal memory footprint suitable for Render free tier (512MB RAM)
- No heavy libraries used

---

## [Version 2.4.0] - 2026-03-08

### New Features - Quiz System

#### 1. Question Selection System
- Added checkbox selection for each question in preview page
- Select All / Deselect All buttons
- Selection count display
- Questions stored in session for quiz generation

#### 2. Remove Unwanted MCQ Feature
- Delete button for each question card in preview page
- Removed questions marked visually (grayed out with "Removed" label)
- Removed questions excluded from quiz and exports

#### 3. Quiz Generator
- "Generate Quiz" button on preview page
- Modal to choose quiz type:
  - All Questions (use all selected questions)
  - Random Questions (choose number: 10, 25, 50, 80, 100 or custom)

#### 4. Quiz Interface (New quiz.html)
- Mobile responsive full-screen layout
- One question at a time display
- Clickable options with immediate feedback
- Correct (green) / Wrong (red) highlighting
- Previous and Next navigation buttons
- Full-screen toggle button

#### 5. Quiz Progress Bar
- Horizontal progress bar showing completion
- Two colors: green for correct, red for wrong answers
- Percentage displayed inside the bar
- Stats: correct/wrong count display

#### 6. Question Shuffle
- Questions shuffled randomly when quiz starts
- Different order each time

#### 7. Option Shuffle
- Options randomized within each question
- Correct answer mapping maintained

#### 8. Quiz Result Screen
- Correct answers count
- Wrong answers count
- Percentage score
- Performance messages based on score:
  - 90-100%: "Excellent! Outstanding performance!"
  - 80-89%: "Great job! Well done!"
  - 70-79%: "Good work! Keep it up!"
  - 60-69%: "Not bad! Room for improvement."
  - 50-59%: "Fair attempt. Try again!"
  - Below 50%: "Keep practicing!"

#### 9. Restart Quiz Options
- Restart with same questions (shuffled)
- New random questions option

#### 10. Exam Mode Features (Infrastructure)
- Tab switching detection with warning
- Auto-submit after 3 tab switches
- Anti-cheat measures:
  - Right-click disabled
  - Copy/paste disabled
  - Long-press disabled on mobile
  - Text selection disabled

### Files Added
- `quiz.html` - New quiz interface page
- `css/quiz.css` - Quiz-specific styles
- `js/quiz.js` - Quiz logic and functionality

### Files Modified
- `preview.html` - Added selection controls, quiz modal
- `css/styles.css` - Added selection and quiz styles
- `js/preview.js` - Added selection, deletion, quiz generation

### Notes
- All quiz functionality is frontend-driven (no additional API calls)
- Questions shuffled for each quiz attempt
- Ready for GitHub Pages and Render deployment

---

## [Version 2.3.2] - 2026-03-08

### Security Improvements

#### 1. File Size Limit (20MB)
- **Backend**: Increased MAX_CONTENT_LENGTH from 10MB to 20MB
- **File Validator**: Updated MAX_FILE_SIZE to 20MB
- **Frontend**: Updated JavaScript validation to 20MB
- **UI**: Updated "Max 10MB" to "Max 20MB" in index.html

#### 2. Page Limit (50 pages)
- Added `MAX_PDF_PAGES = 50` in config
- Added `validate_page_count()` method in FileValidator
- Page count validation after PDF upload
- Returns error if PDF exceeds 50 pages

#### 3. Rate Limiting
- Implemented in-memory rate limiter in upload.py
- **Limit**: 15 uploads per minute per IP
- Returns 429 status when exceeded
- Uses timestamp-based tracking with automatic cleanup

#### 4. Temporary File Cleanup
- Added `cleanup_old_files()` function
- Automatically deletes PDF files older than 1 hour
- Runs on module load and after each upload
- Prevents disk storage overflow on Render

#### 5. Error Handling
- All error responses use standardized format: `{"success": false, "message": "..."}`
- Created `create_error_response()` helper function

#### 6. Preview Page Routing Fix
- Added `/preview.html` route in app.py
- Fixed redirect issue after upload

### Files Modified
- `backend/config.py` - MAX_CONTENT_LENGTH = 20MB, MAX_PDF_PAGES = 50
- `backend/utils/file_validator.py` - MAX_FILE_SIZE = 20MB, MAX_PAGES = 50, validate_page_count()
- `backend/routes/upload.py` - Rate limiting, cleanup, error handling, page validation
- `backend/app.py` - Added /preview.html route
- `js/upload.js` - Updated validation to 20MB
- `index.html` - Updated "Max 20MB"

### Privacy Protection (.gitignore already has)
- `storage/uploaded_pdfs/` - PDF files protected from git
- `storage/generated_json/` - JSON files protected from git
- `.env` - Environment variables protected
- `*.db` - Database files protected

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
