# MCQ Extractor AI - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Feature List](#feature-list)
3. [System Architecture](#system-architecture)
4. [AI Usage Policy](#ai-usage-policy)
5. [Export Architecture](#export-architecture)
6. [Quiz System Documentation](#quiz-system-documentation)
7. [Statistics System](#statistics-system)
8. [Deployment Notes](#deployment-notes)
9. [File Structure](#file-structure)
10. [API Documentation](#api-documentation)

---

## Project Overview

**MCQ Extractor AI** is a web application that extracts Multiple Choice Questions (MCQs) from PDF files using artificial intelligence.

### What It Does:
1. **Upload PDF** - User uploads a PDF file containing questions
2. **AI Extraction** - AI reads and extracts all MCQs with options and correct answers
3. **Structured Data** - Returns JSON with questions, 4 options, and correct answer index
4. **Export Options** - Download in multiple formats or generate quizzes

### Simple Flow:
```
PDF Upload → AI Extraction → Structured MCQs → Export/Quiz
```

---

## Feature List

### Core Features:
- ✅ **PDF to MCQ Extraction** - Uses AI to extract questions from PDF files
- ✅ **MASTER JSON System** - Central JSON storage for all extracted MCQs
- ✅ **Multi Format Export** - Export to JSON, CSV, TXT, Markdown, HTML, XML, YAML, SQL, Aiken, GIFT, Excel
- ✅ **Print-Ready Exports** - Question Paper PDF, Answer Key PDF, OMR Sheet PDF, Tabular PDF, DOCX

### Quiz Features:
- ✅ **Question Filtering** - Filter questions in preview
- ✅ **Remove Unwanted MCQs** - Delete unwanted questions from selection
- ✅ **Question Selection** - Select specific questions for quiz
- ✅ **Quiz Generator** - Generate quizzes from selected questions
- ✅ **Random Quiz Generation** - Generate random subset quizzes (10, 25, 50, 80, 100 or custom)
- ✅ **Exam Mode** - Timer-based exam with anti-cheat measures
- ✅ **Quiz Progress Bar** - Visual progress indicator with correct/wrong counts
- ✅ **Restart Quiz Option** - Restart with same or new random questions

### UI/UX Features:
- ✅ **Like/Dislike System** - Users can vote on the application
- ✅ **View Counter** - Tracks total PDF extractions
- ✅ **Social Links Integration** - GitHub, Instagram, Telegram links
- ✅ **Responsive UI** - Works on mobile, tablet, and desktop

---

## System Architecture

### Pipeline Flow:

```
┌─────────────────┐
│   Upload PDF    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PDF Reader     │  ← pypdf extracts text from PDF
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AI Processor    │  ← Groq Llama 3.1 8B model
│ (GROQ API)      │    processes text → MCQs
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ JSON Formatter  │  ← Validates & cleans data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MASTER JSON     │  ← Central storage
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│Export │ │ Quiz  │
│System │ │System │
└───────┘ └───────┘
```

### Detailed Steps:

1. **PDF Upload** - User uploads PDF via `/api/upload/file`
2. **PDF Reader** - Backend reads text using pypdf
3. **AI Processor** - Sends text to GROQ API (Llama 3.1 8B)
4. **JSON Formatter** - Validates and structures MCQ data
5. **MASTER JSON** - Saves to `storage/generated_json/`
6. **Export/Quiz** - User exports or generates quiz

---

## AI Usage Policy

### AI is ONLY used for:
- **PDF → MCQ Extraction** - Converting PDF text to structured MCQs

### NOT using AI for:
- ❌ Quiz generation (all local JavaScript)
- ❌ Export formats (all local Python)
- ❌ Filtering questions (all local JavaScript)
- ❌ Statistics (all local JSON storage)

### Benefits:
- Minimal AI calls (only 1 per PDF)
- Lower costs (GROQ free tier lasts longer)
- Faster operations (exports & quiz are instant)
- Works offline for exports (no API needed)

---

## Export Architecture

### Export Pipeline:

```
MASTER JSON
    │
    ▼
┌─────────────────┐
│ export_service  │  ← Python export module
└────────┬────────┘
         │
    ┌────┴────────────────────────────┐
    ▼    ▼     ▼     ▼      ▼     ▼      ▼
┌────┐ ┌───┐ ┌───┐ ┌────┐ ┌───┐ ┌────┐ ┌───┐
│JSON│ │CSV│ │TXT│ │HTML│ │XML│ │YAML│ │SQL│
└────┘ └───┘ └───┘ └────┘ └───┘ └────┘ └───┘
    │    │    │     │     │     │     │
    └────┴────┴─────┴─────┴─────┴─────┘
                    │
                    ▼
               ┌──────────┐
               │   20+     │
               │  Formats │
               └──────────┘
```

### Available Export Formats:

**Digital Formats:**
| Format | Description |
|--------|-------------|
| JSON | Raw MCQ data |
| CSV | Spreadsheet format |
| TXT | Plain text |
| Markdown | Formatted text |
| HTML | Web page |
| XML | Structured data |
| YAML | Configuration format |
| SQL | Database insert |
| Aiken | Moodle format |
| GIFT | Moodle import |
| Excel | Spreadsheet |

**Print-Ready Formats:**
| Format | Description |
|--------|-------------|
| Question Paper PDF | Print without answers |
| Answer Key PDF | Teacher's copy |
| OMR Sheet PDF | Bubble answer sheets |
| Tabular PDF | Table format |
| DOCX | Word document |

---

## Quiz System Documentation

### Quiz Generation Flow:

```
Extracted MCQs (from Preview)
         │
         ▼
┌─────────────────────────┐
│   Question Selection    │  ← User selects questions
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Quiz Configuration   │  ← All or Random
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Quiz Generator        │  ← Generates quiz session
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Quiz Interface        │  ← One question at a time
│   (quiz.html)           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Result Screen         │  ← Shows score + message
└─────────────────────────┘
```

### Quiz Features:

1. **Question Selection** - Checkbox selection in preview
2. **Select All/Deselect All** - Quick selection buttons
3. **Remove Unwanted** - Delete questions before quiz
4. **Quiz Types:**
   - All Questions - Use all selected questions
   - Random - Choose specific number (10, 25, 50, 80, 100, custom)

5. **Quiz Interface:**
   - One question at a time
   - Clickable options with instant feedback
   - Correct (green) / Wrong (red) highlighting
   - Previous/Next navigation
   - Progress bar with percentage

6. **Result Screen:**
   - Correct/Wrong count
   - Percentage score
   - **26+ Compliment Messages** (randomly selected)
   - Restart options

### Quiz Result Messages (26+ Messages):

| Score Range | Messages |
|-------------|----------|
| 90-100% | "Perfect Score!", "Outstanding!", "Marvelous!", "Phenomenal!", "Excellent!" |
| 80-89% | "Awesome!", "Superb!", "Impressive!", "Terrific!", "Great Job!" |
| 70-79% | "Well Done!", "Nice Work!", "Great Effort!", "Thumbs Up!", "Good Work!" |
| 60-69% | "Decent Job!", "Nice Try!", "Keep Going!", "Not Bad!", "Good!" |
| 50-59% | "Almost There!", "Good Start!", "Keep Trying!", "Fair Attempt!" |
| Below 50% | "Don't Give Up!", "Stay Positive!", "Keep Learning!", "You Can Do It!" |

---

## Statistics System

### Statistics Tracked:

| Stat | Trigger | Storage |
|------|---------|---------|
| **Views** | Every PDF extraction | `storage/stats.json` |
| **Likes** | User clicks like button | `storage/stats.json` |
| **Dislikes** | User clicks dislike button | `storage/stats.json` |

### Rules:

1. **Views:**
   - Automatically increments when `/api/extract` is called
   - Tracks total PDF extractions

2. **Likes:**
   - Increments when user clicks ❤️ button
   - Protected by browser localStorage (1 vote per browser)

3. **Dislikes:**
   - Increments when user clicks 👎 button
   - Protected by browser localStorage (1 vote per browser)

### Anti-Spam Protection:
- Uses browser localStorage to track votes
- Same browser cannot vote multiple times
- Buttons disabled after voting with visual feedback

---

## Deployment Notes

### Optimized for Render Free Tier:

| Resource | Limit | Optimization |
|----------|-------|--------------|
| **RAM** | 512MB | Lightweight libraries (~7MB) |
| **Bandwidth** | 750 hours/month | Minimal AI calls |
| **Disk** | 1GB | Auto-cleanup after 1 hour |

### Performance Optimizations:

1. **Minimal AI Usage:**
   - Only 1 API call per PDF
   - No AI for exports (all local Python)
   - No AI for quiz (all local JavaScript)

2. **Lightweight Libraries:**
   - pypdf (PDF reading)
   - reportlab (PDF generation)
   - python-docx (Word docs)
   - openpyxl (Excel)

3. **File Cleanup:**
   - Auto-delete PDFs older than 1 hour
   - Auto-delete JSON after download option

4. **Token Optimization:**
   - Groq Llama 3.1 8B (efficient model)
   - Optimized prompts for minimal tokens
   - Production: Llama 3.3 70B for quality

---

## File Structure

```
mcq-extractor-ai/
│
├── 🖥️  frontend/              # Web UI (HTML/CSS/JS)
│   ├── index.html             # Upload page
│   ├── preview.html           # Results page with export options
│   ├── quiz.html              # Quiz interface
│   ├── css/
│   │   ├── styles.css         # Main styling
│   │   └── quiz.css           # Quiz-specific styles
│   └── js/
│       ├── upload.js          # File upload handling
│       ├── preview.js         # MCQ display, selection, export
│       ├── quiz.js            # Quiz logic & result messages
│       ├── stats.js           # Statistics display & voting
│       ├── download.js        # Download functionality
│       └── status.js          # Status messages
│
├── ⚙️   backend/              # Server (Python/Flask)
│   ├── app.py                # Main Flask application
│   ├── config.py             # Configuration (API keys, limits)
│   ├── routes/               # API endpoints
│   │   ├── upload.py         # POST /api/upload/file
│   │   ├── extract.py       # POST /api/extract/<file_id>
│   │   ├── download.py      # GET /api/download/*
│   │   ├── stats.py         # GET/POST /api/stats/*
│   │   └── validate.py      # POST /api/validate
│   ├── services/             # Core business logic
│   │   ├── ai_processor.py   # Groq AI integration
│   │   ├── pdf_reader.py    # PDF text extraction
│   │   ├── json_formatter.py # Format & validate MCQs
│   │   ├── export_service.py # Export to all formats
│   │   └── storage_service.py # File I/O operations
│   ├── models/               # Database models
│   │   ├── database.py
│   │   ├── mcq_model.py
│   │   └── pdf_model.py
│   └── utils/               # Helper utilities
│       ├── error_handler.py
│       ├── file_validator.py
│       └── helpers.py
│
├── 💾  storage/              # File storage
│   ├── uploaded_pdfs/        # Uploaded PDFs (auto-cleaned)
│   ├── generated_json/        # Output JSON files
│   └── stats.json            # Statistics data
│
├── 📊  database/             # SQLite database
├── 📝  requirements.txt       # Python packages
├── 🚀  run.py               # Application entry point
├── 🔧  render.yaml          # Render deployment config
└── 📚  Documentation         # README, CHANGELOG, etc.
```

---

## API Documentation

### Core Endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/file` | POST | Upload PDF file |
| `/api/extract/<file_id>` | POST | Extract MCQs from PDF |
| `/api/download/<file_id>` | GET | Download original JSON |
| `/api/download/export/<format>/<file_id>` | GET | Export in specified format |
| `/api/download/list` | GET | List all files |
| `/api/download/export/formats` | GET | Get supported formats |
| `/api/health` | GET | Server health check |

### Statistics Endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Get current statistics |
| `/api/stats/like` | POST | Increment likes |
| `/api/stats/dislike` | POST | Increment dislikes |
| `/api/stats/view` | POST | Increment views (auto-called) |

### Export Formats:

```
/api/download/export/json/<file_id>      # JSON
/api/download/export/csv/<file_id>       # CSV
/api/download/export/txt/<file_id>       # TXT
/api/download/export/markdown/<file_id>  # Markdown
/api/download/export/html/<file_id>      # HTML
/api/download/export/xml/<file_id>       # XML
/api/download/export/yaml/<file_id>      # YAML
/api/download/export/sql/<file_id>       # SQL
/api/download/export/aiken/<file_id>     # Aiken format
/api/download/export/gift/<file_id>      # GIFT format
/api/download/export/excel/<file_id>     # Excel (XLSX)

/api/download/export/question_pdf/<file_id>    # Question Paper PDF
/api/download/export/answer_key_pdf/<file_id>  # Answer Key PDF
/api/download/export/omr_pdf/<file_id>         # OMR Sheet PDF
/api/download/export/tabular_pdf/<file_id>     # Tabular PDF
/api/download/export/docx/<file_id>            # DOCX Question Paper
```

---

## Quick Start

### Local Development:

```bash
# Clone
git clone https://github.com/saurabh7429/mcq-extractor-ai.git
cd mcq-extractor-ai

# Create venv
python -m venv venv
venv\Scripts\activate  # Windows

# Install
pip install -r requirements.txt

# Setup API key
copy .env.example .env
# Edit .env: GROQ_API_KEY=your_key

# Run
python run.py

# Open
http://localhost:5000
```

### Deploy to Render:

1. Push to GitHub
2. Create Web Service on Render.com
3. Add `GROQ_API_KEY` environment variable
4. Deploy!

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Empty results | Use text-based PDF (not scanned) |
| API error | Check GROQ_API_KEY in .env |
| CORS error | Check API_BASE_URL in frontend |
| File too big | Compress PDF (<20MB, <50 pages) |
| Slow response | First request on Render is slow (free tier) |

---

Made with ❤️ using Flask + GROQ AI

