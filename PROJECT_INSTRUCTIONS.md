# MCQ Extractor AI - Complete Project Manual

**Last Updated:** March 5, 2026  
**Version:** 2.0.0 (Interactive UI)  
**Status:** Production Ready  
**Owner:** Saurabh

---

## 🎯 Project Overview

**MCQ Extractor AI** is a sophisticated full-stack web application that automatically extracts multiple-choice questions (MCQs) from PDF documents using AI (Google Gemini).

### ✨ Key Features:
- ✅ Drag-and-drop PDF upload with validation (max 10MB, PDF only)
- ✅ AI-powered MCQ extraction using Google Gemini API
- ✅ Interactive preview with search/filter functionality
- ✅ Inline editing of questions and answer options
- ✅ Toggle correct answers with one click
- ✅ Download extracted MCQs as JSON
- ✅ Copy MCQs to clipboard
- ✅ Toast notifications and progress tracking
- ✅ SQLite database for metadata persistence
- ✅ Responsive design (mobile & desktop optimized)
- ✅ Production-ready with logging and error handling

---

## 🔗 Live Deployment

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | https://saurabh7429.github.io/mcq-extractor-ai/ | Interactive UI (GitHub Pages) |
| **Backend** | https://mcq-extractor-backend.onrender.com | Python Flask API (Render) |
| **Repository** | https://github.com/saurabh7429/MCQ-extractor-ai | Source Code & Issues |

---

## 🏗️ System Architecture

### Data Flow
```
User Browser
    ↓
[FRONTEND] HTML/CSS/JS (GitHub Pages)
    ├─ index.html → upload interface
    ├─ preview.html → results interface
    ├─ js/config.js → API configuration
    ├─ js/upload.js → upload & validation logic
    ├─ js/preview.js → display, search, edit, filter
    ├─ js/download.js → file downloads
    └─ css/styles.css → responsive styling
    │
    ├─ HTTP/CORS API Calls ──→
    │
[BACKEND] Flask Python (Render.com)
    ├─ Routes (blueprints):
    │  ├─ /api/upload/file → save PDF + generate UUID
    │  ├─ /api/extract/process → extract text → call Gemini AI
    │  ├─ /api/extract/preview → return stored MCQs JSON
    │  ├─ /api/download/json → stream JSON file
    │  └─ /api/health → health check
    │
    ├─ Services (business logic):
    │  ├─ pdf_reader.py → extract text using pdfplumber
    │  ├─ ai_processor.py → call Google Gemini API
    │  ├─ json_formatter.py → validate MCQ format
    │  └─ storage_service.py → file I/O operations
    │
    ├─ Data Persistence:
    │  ├─ database/mcq.db → SQLite (pdf_files, mcqs tables)
    │  ├─ storage/uploaded_pdfs/ → original PDFs (UUID-named)
    │  └─ storage/generated_json/ → extracted MCQs JSON
    │
    └─ External APIs:
       └─ Google Gemini API (gemini-2.5-flash) → MCQ extraction
```

---

## 📁 Complete File Structure

```
mcq-extractor-ai/
├── 📄 INSTRUCTION.md                # Original instructions
├── 📄 PROJECT_INSTRUCTIONS.md       # This comprehensive guide
├── 📄 DETAILS.md                    # Architecture & pros/cons
├── 📄 index.html                    # Upload page (frontend)
├── 📄 preview.html                  # Preview page (frontend)
├── 📄 run.py                        # Entry point (python run.py)
├── 📄 requirements.txt              # Python dependencies
├── 📄 render.yaml                   # Render deployment config
├── 📄 .env.example                  # Example environment variables
├── 📄 .gitignore                    # Git ignore rules
│
├── 📁 js/ (served from root)
│   ├── config.js                    # API_BASE_URL & endpoints
│   ├── upload.js                    # Drag-drop, validation, upload
│   ├── preview.js                   # Display, search, edit, filter
│   ├── download.js                  # File download utilities
│   └── status.js                    # Loading states & toasts
│
├── 📁 css/
│   └── styles.css                   # Global responsive styles
│
├── 📁 frontend/ (Flask serves these)
│   ├── index.html
│   ├── preview.html
│   ├── js/
│   │   ├── config.js
│   │   ├── upload.js
│   │   ├── preview.js
│   │   ├── download.js
│   │   └── status.js
│   └── css/
│       └── styles.css
│
├── 📁 backend/
│   ├── __init__.py
│   ├── app.py                       # Flask app factory
│   ├── config.py                    # Config by environment
│   │
│   ├── routes/
│   │   ├── upload.py                # /api/upload/file
│   │   ├── extract.py               # /api/extract/process, preview
│   │   ├── download.py              # /api/download/json, pdf
│   │   └── validate.py              # /api/validate
│   │
│   ├── services/
│   │   ├── pdf_reader.py            # Extract text (pdfplumber)
│   │   ├── ai_processor.py          # Gemini API calls
│   │   ├── json_formatter.py        # Validate MCQ JSON
│   │   └── storage_service.py       # File operations
│   │
│   ├── models/
│   │   ├── database.py              # DB init & connection
│   │   ├── mcq_model.py             # MCQ table model
│   │   └── pdf_model.py             # PDF file table model
│   │
│   └── utils/
│       ├── error_handler.py         # Custom exceptions
│       ├── file_validator.py        # File validation logic
│       └── helpers.py               # Utility functions
│
├── 📁 database/
│   └── mcq.db                       # SQLite file (auto-created)
│
├── 📁 storage/
│   ├── uploaded_pdfs/               # Original PDFs (UUID-named)
│   └── generated_json/              # Extracted MCQs JSON
│
├── 📁 logs/                         # Application logs
│   └── app.log                      # Rotating log file
│
└── 📁 tests/
    ├── test_routes.py
    ├── test_ai_processor.py
    ├── test_pdf_reader.py
    └── test_json_formatter.py
```

---

## 🖥️ Frontend - How It Works

### Upload Page (index.html)

**User Experience:**
1. User opens frontend URL
2. Sees drag-and-drop zone with animated icon
3. Can drag PDF or click to browse
4. File is validated (must be PDF, ≤10MB)
5. File info displayed (name, size)
6. Click "Upload & Extract" button
7. Progress bar animates showing upload → extraction → saving
8. On success → redirected to preview.html

**JavaScript Flow (js/upload.js):**
```javascript
1. Drag/drop event listeners on dropZone
2. File validation:
   - Check MIME type (application/pdf)
   - Check file size (≤10MB)
   - Check extension (.pdf)
3. Display selected file with info
4. Enable upload button
5. On upload click:
   a. POST to /api/upload/file (FormData with file)
   b. Get file_id from response
   c. POST to /api/extract/process (with file_id)
   d. Wait for extraction complete
   e. Store file_id in sessionStorage
   f. Redirect to preview.html
```

### Preview Page (preview.html) - NEW INTERACTIVE FEATURES

**User Experience:**
1. Page loads with spinner
2. Fetches MCQ data via /api/extract/preview
3. Displays MCQ cards in grid layout
4. Search box to filter questions/options
5. Statistics shows count or "X of Y" if filtered

**Interactive Features:**
- 🖱️ **Double-click question text** → enters edit mode (contentEditable)
- 🖱️ **Double-click option text** → enters edit mode
- 🖱️ **Click an option** → marks as correct answer
- ✏️ **Editable elements** show dashed border + golden background
- 💾 **Auto-save on blur** → changes stored in memory
- 📋 **Copy JSON** → clipboard copy of current MCQs
- ⬇️ **Download JSON** → downloads file (respects edits/filters)

**JavaScript Logic (js/preview.js):**
```javascript
1. Page loads, get file_id from sessionStorage
2. POST /api/extract/preview → get MCQ array
3. Render MCQ cards:
   - Question displayed with index number
   - 4 options in grid/list
   - Correct option highlighted green
4. Attach event listeners:
   - Click on option → update correct_answer index → re-render
   - Double-click on text → contentEditable=true, add editing styles
   - Blur event → save changes to mcqData array
   - Search input → filter MCQs in real-time
5. Copy/Download buttons:
   - Copy: JSON.stringify(mcqData) → clipboard
   - Download: Create blob → trigger download
```

### Configuration (js/config.js)

```javascript
API_BASE_URL: 'https://mcq-extractor-backend.onrender.com'  // Production
// Change to 'http://localhost:5000' for local development

// Endpoints:
/api/upload/file
/api/extract/process
/api/extract/preview
/api/download/json
/api/health
```

---

## ⚙️ Backend - How It Works

### Main Entry Point (run.py)

```python
python run.py
# Starts Flask development server on 0.0.0.0:5000
# Or use: gunicorn backend.app:app (for Render production)
```

### Configuration (backend/config.py)

```python
# Loaded from .env file
FLASK_ENV = 'production' or 'development'
GEMINI_API_KEY = 'your-api-key'
SECRET_KEY = 'random-string'

# Storage paths:
# Local: storage/uploaded_pdfs/, storage/generated_json/
# Render: /tmp/storage/... (ephemeral)

# Database:
# Local: database/mcq.db
# Render: /tmp/mcq.db
```

### API Routes & Flow

#### 1️⃣ Upload File
```
POST /api/upload/file
Content-Type: multipart/form-data

Request:
  file: <PDF file>

Response (200):
{
  "status": "success",
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "test.pdf",
  "size": "2.5 MB"
}

Backend Process:
  1. Validate file (type, size, MIME)
  2. Generate UUID for file_id
  3. Sanitize filename
  4. Save to storage/uploaded_pdfs/{UUID}_{filename}
  5. Save metadata to database (pdf_files table)
  6. Return file_id
```

#### 2️⃣ Extract MCQs
```
POST /api/extract/process
Content-Type: application/json

Request:
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000"
}

Response (200):
{
  "status": "success",
  "message": "MCQs extracted successfully",
  "count": 15
}

Backend Process:
  1. Get file_id from request
  2. Retrieve PDF path from storage
  3. Read PDF using PDFReader (pdfplumber):
     - Extract text from all pages
     - Clean text (remove special chars, newlines)
  4. Call AIProcessor:
     - Split text into chunks (if >10K chars)
     - Send to Gemini API with extraction prompt
     - Parse JSON response
     - Validate each MCQ (has 4 options, correct_answer 0-3)
     - Merge results from all chunks
  5. Save formatted JSON to storage/generated_json/{file_id}.json
  6. Save MCQ records to database (mcqs table)
  7. Return success response
```

#### 3️⃣ Preview MCQs
```
POST /api/extract/preview
Content-Type: application/json

Request:
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000"
}

Response (200):
{
  "status": "success",
  "mcqs": [
    {
      "question": "What is 2+2?",
      "options": ["3", "4", "5", "6"],
      "correct_answer": 1
    },
    ...
  ],
  "count": 15
}

Backend Process:
  1. Get file_id
  2. Read stored JSON file from storage/generated_json/
  3. Parse JSON array
  4. Return MCQs
```

#### 4️⃣ Download JSON
```
POST /api/download/json
Content-Type: application/json

Request:
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000"
}

Response (200):
Content-Type: application/json
Content-Disposition: attachment; filename="550e8400...json"

[{...MCQs...}]

Backend Process:
  1. Get file_id
  2. Find JSON file
  3. Stream as file attachment
```

#### 5️⃣ Health Check
```
GET /api/health

Response (200):
{
  "status": "healthy",
  "service": "MCQ Extractor AI",
  "version": "1.0.0"
}
```

### Services (Business Logic)

#### PDFReader (services/pdf_reader.py)
```python
# Extract text from PDF files
from backend.services.pdf_reader import PDFReader

reader = PDFReader()
text = reader.read_pdf('path/to/file.pdf')
# Returns: cleaned text string

# Uses pdfplumber library for text extraction
# Handles:
# - Multi-page PDFs
# - Text cleaning (remove junk chars)
# - Raises PDFReadError if no text
```

#### AIProcessor (services/ai_processor.py)
```python
# Extract MCQs using Google Gemini API
from backend.services.ai_processor import AIProcessor

processor = AIProcessor()
mcqs = processor.extract_mcq(text)
# Returns: list of MCQ dicts

# Logic:
# - Calls Gemini API (gemini-2.5-flash model)
# - Sends extraction prompt
# - Parses & validates JSON response
# - Handles large text by chunking
# - Retries up to 3 times on failure

# Expected MCQ format:
[
  {
    "question": "Question text",
    "options": ["A", "B", "C", "D"],
    "correct_answer": 0  # Index 0-3
  }
]
```

#### JSONFormatter (services/json_formatter.py)
```python
# Validate and format MCQ JSON
from backend.services.json_formatter import JSONFormatter

formatter = JSONFormatter()
valid_mcqs = formatter.format_mcqs(mcq_data)
# Returns: validated list of MCQs

# Checks:
# - Each MCQ has question, options, correct_answer
# - Options has exactly 4 elements
# - correct_answer is 0-3
# - No duplicates
```

#### StorageService (services/storage_service.py)
```python
# Manage file I/O
from backend.services.storage_service import StorageService

storage = StorageService()

# Save uploaded PDF
path = storage.save_upload(file, 'filename.pdf')

# Save generated JSON
storage.save_json(file_id, mcq_list)

# Retrieve files
pdf_path = storage.get_pdf_by_uuid(file_id)
json_path = storage.get_json_by_uuid(file_id)
```

---

## 🔑 Environment Variables

### Required for Backend

**Gemini API Key:**
```env
GEMINI_API_KEY=your-google-gemini-api-key-here
```
- Get from: https://aistudio.google.com/app/apikey
- Free tier available for testing
- Copy your API key here

**Flask Settings:**
```env
FLASK_ENV=production        # or: development, testing
FLASK_DEBUG=0               # 1=enabled, 0=disabled
SECRET_KEY=generate-random-string-here
```

**Optional:**
```env
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
FLASK_HOST=0.0.0.0          # Default binding
FLASK_PORT=5000             # Default port
RENDER=1                    # Auto-set on Render deployment
```

### How to Generate SECRET_KEY

```bash
python -c "import os; print(os.urandom(24).hex())"
# Output: abc123def456...
# Copy this value to SECRET_KEY in .env
```

### .env File Location

```
mcq-extractor-ai/
├── .env                     # Development (git-ignored)
├── .env.example             # Template (committed)
└── Render Dashboard         # Production (web UI)
```

---

## 🚀 Setup & Deployment

### 1. Local Development Setup

```bash
# Clone repository
git clone https://github.com/saurabh7429/MCQ-extractor-ai.git
cd mcq-extractor-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env and add GEMINI_API_KEY

# Start server
python run.py
# Server runs on http://localhost:5000
```

### 2. Frontend Deployment (GitHub Pages)

**Steps:**
1. Push code to GitHub main branch
2. Repository Settings → Pages
3. Source: Deploy from branch
4. Branch: main
5. Folder: / (root)
6. Save
7. Site published at: https://saurabh7429.github.io/mcq-extractor-ai/

**Important:** Update API URL in `js/config.js` before pushing:
```javascript
API_BASE_URL: 'https://mcq-extractor-backend.onrender.com'
```

### 3. Backend Deployment (Render)

**Steps:**
1. Go to https://render.com
2. Sign up (GitHub login)
3. New → Web Service
4. Connect GitHub repository
5. Settings:
   ```
   Name: mcq-extractor-backend
   Runtime: Python 3.11
   Region: Closest to you
   Build Command: pip install -r requirements.txt
   Start Command: python run.py
   ```
6. Environment Variables (go to Render dashboard):
   ```
   GEMINI_API_KEY=your-api-key-here
   SECRET_KEY=generate-random-string
   FLASK_ENV=production
   ```
7. Deploy → Wait 2-5 minutes
8. Backend URL: https://mcq-extractor-backend.onrender.com

**Notes:**
- Render free tier has 15-minute sleep after inactivity
- Ephemeral filesystem (files deleted on restart)
- Upgrade for persistent storage if needed

---

## 🧪 Testing

### Manual Testing Workflow

```
1. Upload Test:
   - Open frontend
   - Drag or browse PDF file
   - Verify file info shows
   - Click "Upload & Extract"
   - Check loading animation

2. Extraction Test:
   - Monitor progress bar
   - Should complete 5-30 seconds
   - Auto-redirect to preview page

3. Preview Test:
   - See MCQ cards rendered
   - Count matches extracted MCQs
   - Try search (type in search box)
   - Try filter (results update live)
   - Try edit (double-click text)
   - Try toggle answer (click option)

4. Download Test:
   - Click "Copy JSON" → check clipboard
   - Click "Download JSON" → check file

5. Health Check:
   curl https://mcq-extractor-backend.onrender.com/api/health
   Response: {"status": "healthy", ...}
```

### Unit Tests

```bash
python -m pytest tests/ -v
# Run all tests with verbose output

# Individual tests:
pytest tests/test_routes.py
pytest tests/test_ai_processor.py
pytest tests/test_pdf_reader.py
pytest tests/test_json_formatter.py
```

---

## 📊 Database Schema

### PDF Files Table
```sql
CREATE TABLE pdf_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'processed'
);
```

### MCQs Table
```sql
CREATE TABLE mcqs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pdf_id INTEGER NOT NULL,
    question VARCHAR(2000) NOT NULL,
    options JSON NOT NULL,
    answer VARCHAR(500) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pdf_id) REFERENCES pdf_files(id) ON DELETE CASCADE
);
```

---

## 🐛 Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| "ModuleNotFoundError: No module named 'flask'" | Dependencies not installed | `pip install -r requirements.txt` |
| "Failed to extract MCQs" | Gemini API key missing/wrong | Check `.env` file GEMINI_API_KEY |
| "No MCQs found" | PDF is scanned image | Need OCR or manual extraction |
| "CORS error" | Backend URL wrong in config.js | Update `API_BASE_URL` in js/config.js |
| "Render: Cannot access /tmp" | File permissions | Upgrade to Render Pro plan |
| "Changes lost on refresh" | SessionStorage cleared | Edit only persists in session |
| "Render app sleeps" | Free tier inactivity | Upgrade plan or use keep-alive |

---

## 📦 Dependencies

**Backend (requirements.txt):**
- Flask 3.1.0+ - Web framework
- Flask-CORS 5.0.0+ - CORS support
- SQLAlchemy 2.0.36+ - Database ORM
- google-generativeai 0.8.0+ - Gemini API
- pdfplumber 0.11.0+ - PDF text extraction
- pypdf 5.1.0+ - PDF processing
- Pillow 11.0.0+ - Image processing
- requests 2.32.0+ - HTTP client
- gunicorn 23.0.0+ - Production WSGI
- python-dotenv 1.0.1+ - .env loading

**Frontend:**
- Pure HTML5 + CSS3 + Vanilla JavaScript
- Zero dependencies
- Works in all modern browsers

---

## 💡 Performance Tips

### Frontend:
- SessionStorage for file_id (not localStorage)
- Efficient DOM updates (no full rerenders)
- GPU-accelerated CSS animations
- Responsive grid auto-wraps

### Backend:
- Text chunking for large PDFs
- Connection pooling
- File streaming
- Rotating logs (10MB max)

### Render:
- Use PostgreSQL for persistence
- Use Render Disk for file storage
- Consider background jobs for large PDFs

---

## 🎯 Future Features (v3.0.0)

- [ ] User authentication & accounts
- [ ] Batch PDF processing
- [ ] Export to Excel/CSV/PDF
- [ ] OCR for scanned PDFs
- [ ] Question difficulty classification
- [ ] Duplicate detection
- [ ] Statistics dashboard
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] API rate limiting

---

## 📝 Version History

- **v2.0.0** (Mar 5, 2026) - Interactive preview, search, inline edit
- **v1.0.0** (Mar 1, 2026) - Initial release

---

## 🔗 Resources

- **GitHub:** https://github.com/saurabh7429/MCQ-extractor-ai
- **Gemini API:** https://ai.google.dev/docs
- **Render Docs:** https://render.com/docs
- **Flask Docs:** https://flask.palletsprojects.com
- **SQLAlchemy:** https://sqlalchemy.org

---

**Questions? Open an issue on GitHub or check the DETAILS.md file for architecture overview.**

Happy extracting! 🚀