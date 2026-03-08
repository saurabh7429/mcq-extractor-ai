# MCQ Extractor AI - Complete Project Documentation

## Table of Contents
1. [What is this Project?](#what-is-this-project)
2. [How it Works (Flow)](#how-it-works-flow)
3. [Project Structure](#project-structure)
4. [Technology Stack](#technology-stack)
5. [How to Use](#how-to-use)
6. [How to Update/Modify](#how-to-updatemodify)
7. [Deployment Guide](#deployment-guide)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## What is this Project?

**MCQ Extractor AI** ek web application hai jo PDF files se MCQs (Multiple Choice Questions) extract karta hai using AI.

### Simple Explanation:
1. Tum ek PDF file upload karte ho jisme questions hain
2. AI us PDF ko padhta hai aur questions find karta hai
3. Questions, options aur correct answers JSON format mein milte hain
4. Tum download kar sakte ho ya preview dekh sakte ho

---

## How it Works (Flow)

### Detailed Technical Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE WORKFLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

STEP 1: USER UPLOADS PDF
┌──────────────┐
│ User clicks  │         Browser (index.html)
│ "Upload"     │
└──────┬───────┘
       │ FormData with PDF file
       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. upload.js sends PDF to:                                                  │
│    POST /api/upload/file                                                    │
│                                                                              │
│    Content-Type: multipart/form-data                                        │
│    Body: file (PDF)                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. BACKEND: upload.py                                                      │
│    ┌─────────────────────────────────────────────────────────────────────┐ │
│    │ • Validate file (extension, size, type)                           │ │
│    │ • Generate unique file_id (UUID)                                   │ │
│    │ • Save PDF to: storage/uploaded_pdfs/<uuid>_filename.pdf          │ │
│    │ • Save metadata to database                                        │ │
│    └─────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
       │
       ▼ Returns: {"status": "success", "file_id": "abc-123", ...}
       │
       ▼
STEP 2: EXTRACT MCQs
┌──────────────────────────────────────────────────────────────────────────────┐
│ 3. upload.js sends request to:                                              │
│    POST /api/extract/<file_id>                                             │
│                                                                              │
│    (This can also be a separate call OR embedded in upload response)        │
└──────────────────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 4. BACKEND: extract.py                                                      │
│    ┌─────────────────────────────────────────────────────────────────────┐ │
│    │ a) PDF Reader (pdf_reader.py)                                       │ │
│    │    • Read PDF from: storage/uploaded_pdfs/<uuid>_filename.pdf      │ │
│    │    • Extract text using pypdf library                               │ │
│    │    • Returns: text_content (string), page_count                   │ │
│    │                                                                     │ │
│    │ b) AI Processor (ai_processor.py)                                   │ │
│    │    • Send text to GROQ API                                          │ │
│    │    • Endpoint: https://api.groq.com/openai/v1/chat/completions     │ │
│    │    • Model: llama-3.1-8b-instant                                    │ │
│    │    • Prompt: Extract MCQs from text...                              │ │
│    │    • Returns: raw MCQ data (JSON)                                   │ │
│    │                                                                     │ │
│    │ c) JSON Formatter (json_formatter.py)                               │ │
│    │    • Clean and validate MCQs                                        │ │
│    │    • Ensure 4 options per question                                  │ │
│    │    • Set correct_answer index (0-3)                                │ │
│    │                                                                     │ │
│    │ d) Storage Service (storage_service.py)                             │ │
│    │    • Save JSON to: storage/generated_json/<uuid>.json             │ │
│    │    • Save to database                                               │ │
│    └─────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
       │
       ▼ Returns: {"success": true, "mcqs": [...], "count": 10}
       │
       ▼
STEP 3: SHOW RESULT
┌──────────────┐
│ Browser      │
│ receives JSON│
│ & shows      │
│ preview      │
└──────────────┘
```

### API Calls Detail:

| Call # | URL | Method | Purpose |
|--------|-----|--------|---------|
| 1 | `/api/upload/file` | POST | Upload PDF to server |
| 2 | `/api/extract/<file_id>` | POST | Extract MCQs from PDF |

**Total API Calls: 2**

(First call saves PDF, second call processes and returns MCQs)

### Data Storage Locations:

```
Project Folder/
│
├── storage/
│   ├── uploaded_pdfs/
│   │   └── 744a8cec-e5f2-4921-9516-99a7bd08d08b_test.pdf  ← PDF Yahan
│   │
│   └── generated_json/
│       └── 744a8cec-e5f2-4921-9516-99a7bd08d08b.json     ← MCQs Yahan
│
└── database/
    └── mcq.db  ← Metadata (file_id, filename, timestamps) Yahan
```

### Step-by-Step Data Flow:

```
1. USER ACTION
   │
   ▼
2. JAVASCRIPT (upload.js)
   • Creates FormData object
   • Adds PDF file to it
   • Sends POST request to /api/upload/file
   │
   FLASK SERVER (app.py)
   ▼
3. • Receives request
   • Routes to upload.py
   │
   ▼
4. UPLOAD.PY
   • Validates file (type, size)
   • Generates UUID: 744a8cec-e5f2-4921-9516-99a7bd08d08b
   • Saves to: storage/uploaded_pdfs/744a8cec-e5f2_test.pdf
   • Returns: {"file_id": "744a8cec...", "status": "success"}
   │
   ▼
5. UPLOAD.JS (receives response)
   • Gets file_id from response
   • Calls /api/extract/744a8cec...
   │
   ▼
6. EXTRACT.PY
   • Reads PDF: storage/uploaded_pdfs/744a8cec_test.pdf
   • Extracts text using pypdf
   │
   ▼
7. AI_PROCESSOR.PY
   • Sends text to GROQ API
   • URL: https://api.groq.com/openai/v1/chat/completions
   • Model: llama-3.1-8b-instant
   • Returns: raw MCQ JSON
   │
   ▼
8. JSON_FORMATTER.PY
   • Cleans the data
   • Validates each question has 4 options
   • Sets correct answer index
   │
   ▼
9. STORAGE_SERVICE.PY
   • Saves JSON: storage/generated_json/744a8cec.json
   │
   ▼
10. Returns to browser:
    {"success": true, "mcqs": [...], "count": 10}
    │
    ▼
11. PREVIEW.JS
    • Receives MCQs array
    • Creates HTML cards for each question
    • Displays on preview.html
```

### Database Schema:

```sql
-- PDFs table
CREATE TABLE pdfs (
    id INTEGER PRIMARY KEY,
    file_id TEXT UNIQUE,        -- UUID: 744a8cec-e5f2-4921-9516-99a7bd08d08b
    original_filename TEXT,     -- test.pdf
    stored_filename TEXT,        -- 744a8cec_test.pdf
    file_path TEXT,             -- full path
    file_size INTEGER,          -- bytes
    mime_type TEXT,             -- application/pdf
    page_count INTEGER,         -- number of pages
    created_at TIMESTAMP        -- upload time
);

-- MCQs table
CREATE TABLE mcqs (
    id INTEGER PRIMARY KEY,
    file_id TEXT,               -- links to pdfs table
    question TEXT,              -- question text
    options TEXT,               -- JSON array of options
    correct_answer INTEGER,     -- 0, 1, 2, or 3
    explanation TEXT,           -- optional explanation
    created_at TIMESTAMP
);
```

### Code Flow (File to File):

```
FRONTEND (Browser)
       │
       │ index.html → upload.js
       ▼
BACKEND (Flask)
       │
       ├── app.py (routes request)
       │
       ├── routes/
       │    ├── upload.py (handles file upload)
       │    └── extract.py (handles MCQ extraction)
       │
       ├── services/
       │    ├── pdf_reader.py (reads PDF)
       │    ├── ai_processor.py (calls GROQ API)
       │    └── json_formatter.py (formats response)
       │
       └── storage_service.py (saves files)
              │
              ▼
       storage/ (files on disk)
       database/ (SQLite)
```

### Important Functions:

| File | Function | Purpose |
|------|----------|---------|
| `upload.py` | `upload_file()` | Handle PDF upload |
| `extract.py` | `extract_text_from_file()` | Main extraction logic |
| `pdf_reader.py` | `read_pdf_from_storage(file_id)` | Read PDF and return text |
| `ai_processor.py` | `extract_mcq(text)` | Send to GROQ, get MCQs |
| `json_formatter.py` | `format_mcq(raw_mcqs)` | Clean and validate |
| `storage_service.py` | `save_upload(file, filename)` | Save PDF to disk |
| `storage_service.py` | `save_json_by_uuid(json, file_id)` | Save JSON |

---

## Project Structure

```
mcq-extractor-ai/
│
├── backend/                    # Server-side code (Python/Flask)
│   ├── app.py                  # Main Flask application
│   ├── config.py               # Configuration (API keys, settings)
│   │
│   ├── routes/                 # API Endpoints (URLs)
│   │   ├── upload.py           # POST /api/upload/file - PDF upload
│   │   ├── extract.py          # GET/POST /api/extract/<id> - MCQ extraction
│   │   ├── download.py         # GET /api/download/<id> - JSON download
│   │   └── validate.py         # POST /api/validate - File validation
│   │
│   ├── services/               # Business Logic
│   │   ├── ai_processor.py    # AI se MCQ extract karta hai
│   │   ├── pdf_reader.py       # PDF se text extract karta hai
│   │   ├── json_formatter.py   # JSON format banata hai
│   │   └── storage_service.py  # Files save/load karta hai
│   │
│   ├── models/                 # Database
│   │   ├── database.py         # Database connection
│   │   ├── mcq_model.py       # MCQ data model
│   │   └── pdf_model.py       # PDF data model
│   │
│   └── utils/                 # Helper Functions
│       ├── error_handler.py    # Error handling
│       ├── file_validator.py  # File validation
│       └── helpers.py         # Utility functions
│
├── frontend/                  # User Interface (HTML/CSS/JS)
│   ├── index.html             # Home page (upload PDF)
│   ├── preview.html           # Preview page (show MCQs)
│   ├── css/
│   │   └── styles.css        # Styling
│   └── js/
│       ├── upload.js          # Upload functionality
│       ├── preview.js         # Preview functionality
│       ├── status.js          # Status messages
│       └── download.js        # Download functionality
│
├── storage/                   # File Storage
│   ├── uploaded_pdfs/         # PDFs yahan save hoti hain
│   └── generated_json/        # Generated JSON files
│
├── database/                  # SQLite Database
│   └── mcq.db               # All data yahan save hota hai
│
├── logs/                      # Application Logs
│   └── app.log              # Error logs
│
├── tests/                     # Testing Files
│   ├── test_ai_processor.py
│   ├── test_pdf_reader.py
│   └── test_routes.py
│
├── requirements.txt           # Python packages
├── run.py                    # Application start point
├── .env                      # Environment variables (API keys)
├── render.yaml              # Render deployment config
└── DEPLOY.md                # Deployment guide
```

---

## Technology Stack

### Backend:
| Technology | Purpose |
|------------|---------|
| **Python** | Programming language |
| **Flask** | Web framework (handles API) |
| **GROQ API** | AI service (Llama 3.1 model) |
| **SQLite** | Database |
| **pypdf** | PDF reading |
| **gunicorn** | Production server |

### Frontend:
| Technology | Purpose |
|------------|---------|
| **HTML5** | Page structure |
| **CSS3** | Styling & design |
| **JavaScript** | Interactivity |
| **Fetch API** | API calls |

---

## How to Use

### For Users:
1. **Open Website** → https://mcq-extractor-ai.onrender.com
2. **Upload PDF** → Click or drag-drop PDF file
3. **Wait** → AI process kar raha hai
4. **Preview** → Questions dekh sakte hain
5. **Download** → JSON format mein download kar sakte hain

### For Developers (Local Run):

```bash
# 1. Clone
git clone https://github.com/your-username/mcq-extractor-ai.git
cd mcq-extractor-ai

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install packages
pip install -r requirements.txt

# 4. Create .env file
copy .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here

# 5. Run
python run.py

# 6. Open browser
http://localhost:5000
```

---

## How to Update/Modify

### Common Changes aur Unke Prompts:

#### 1. Change AI Model
**Prompt for AI:**
```
Change the AI model from Llama to another model in ai_processor.py.
Use "mixtral-8x7b-32768" model instead.
```

#### 2. Add New Feature (e.g., Export to Excel)
**Prompt for AI:**
```
Add a new route in backend/routes/download.py to export MCQs to Excel format.
Create a function that converts JSON to Excel using openpyxl library.
```

#### 3. Change Frontend Design
**Prompt for AI:**
```
Update the CSS in frontend/css/styles.css to change the color scheme from 
purple to blue gradient. Also update the button hover effects.
```

#### 4. Add New Validation
**Prompt for AI:**
```
Add file validation in backend/utils/file_validator.py to reject corrupted 
PDF files. Check if file can be opened by pypdf before accepting.
```

#### 5. Change API Response Format
**Prompt for AI:**
```
Modify the response format in backend/routes/extract.py to include 
"category" field for each MCQ. Update json_formatter.py accordingly.
```

#### 6. Add Authentication
**Prompt for AI:**
```
Add basic authentication to the Flask app. Create a simple login system
where users need to enter a password to access the upload feature.
```

#### 7. Add More Question Types
**Prompt for AI:**
```
Update the AI prompt in backend/services/ai_processor.py to also extract
True/False questions along with multiple choice questions.
```

---

## Deployment Guide

### Deploy to Render (Recommended):

1. **Push code to GitHub:**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Go to render.com:**
- Sign in with GitHub
- Click "New" → "Web Service"

3. **Configure:**
- Name: `mcq-extractor-ai`
- Environment: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn backend.app:app --workers 4 --bind 0.0.0.0:$PORT`

4. **Add Environment Variables:**
- `GROQ_API_KEY` = your key (get from https://console.groq.com/keys)

5. **Deploy!** 🎉

---

## Troubleshooting

### Common Issues:

| Problem | Cause | Solution |
|---------|-------|----------|
| Empty [] array | PDF is scanned/image | Use text-based PDF |
| API Error | GROQ_API_KEY not set | Add key in Render |
| CORS Error | Wrong API URL | Check frontend API_BASE_URL |
| File too big | PDF > 10MB | Compress PDF |
| Server Error | Check logs | Check Render logs |

### Check Logs:
```bash
# Local: Check terminal
python run.py

# Render: Go to Dashboard → Logs
```

---

## FAQ

### Q: GROQ_API_KEY kahan se milega?
**A:** https://console.groq.com/keys - Free account create karo aur key copy karo.

### Q: PDF upload nahi ho raha?
**A:** 
- File size 10MB se kam hona chahiye
- Sirf PDF files allowed hain

### Q: MCQs nahi aaye?
**A:**
- PDF text-based hona chahiye (scanned PDFs mein OCR nahi hai)
- GROQ_API_KEY add hona chahiye

### Q: Localhost par kaise chalana hai?
**A:** `python run.py` run karo aur browser mein `localhost:5000` open karo.

### Q: GitHub Pages ka use kyun nahi kar sakte?
**A:** GitHub Pages sirf static files serve karta hai. Python/Flask backend ke liye Render ya Vercel chahiye.

---

## File Descriptions

### Important Files:

| File | Kya Karta Hai |
|------|---------------|
| `app.py` | Flask app create karta hai, routes register karta hai |
| `config.py` | Settings load karta hai (API keys, paths) |
| `ai_processor.py` | AI ko text bhejta hai, MCQs leta hai |
| `pdf_reader.py` | PDF se text extract karta hai |
| `upload.js` | Frontend se file upload handle karta hai |
| `preview.js` | MCQs display karta hai |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/file` | POST | PDF upload karta hai |
| `/api/extract/<file_id>` | GET/POST | MCQs extract karta hai |
| `/api/download/<filename>` | GET | JSON download karta hai |
| `/api/health` | GET | Server status check |

---

## Environment Variables

| Variable | Kya Hai | Kahan Use Hota Hai |
|----------|---------|-------------------|
| `GROQ_API_KEY` | AI service key | ai_processor.py |
| `SECRET_KEY` | Flask security | app.py |
| `FLASK_ENV` | production/development | app.py |
| `LOG_LEVEL` | INFO/DEBUG | app.py |

---

## Credits

- **AI:** GROQ (Llama 3.1 8B Model)
- **Framework:** Flask
- **PDF:** pypdf, pdfplumber
- **Deployment:** Render

---

Made with ❤️ for education

