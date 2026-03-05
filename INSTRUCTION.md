instructions -{
   
   i will uploaded frontend on github and backend on render.com so update like that so project run properly after deployment and also update the links of frontend and backend in this file and also update the link of github repository in this file

   update this file every time when promting with ai 
   update version of project and date of update
   at home page show last update time and version of project
   before work read this file 
   and after work add new lines of update into this file 
   always write in this file what you have done in this project and what you have added or changed in the project
   when you are adding new features or changing existing features then write in this file about that feature and how it is working and what is the use of that feature
   update change log in this file and also update the version of project in this file
   update instruction also in this file and write about how to use the project and how to deploy the project and how to test the project and also write about the architecture of the project and also write about the pros and cons of the project and also write about the deployment diagram of the project and also write about the additional notes of the project
}

# MCQ Extractor AI - Complete Project Manual

**Last Updated:** March 5, 2026  
**Version:** 2.0.0 (Interactive UI)  
**Status:** Production Ready

---

## 🎯 Project Overview

**MCQ Extractor AI** is a sophisticated full-stack web application that automatically extracts multiple-choice questions (MCQs) from PDF documents using AI (Google Gemini). The app features:
- ✅ Drag-and-drop PDF upload with validation
- ✅ AI-powered MCQ extraction from text-based PDFs
- ✅ Interactive preview with search/filter functionality
- ✅ Inline editing of questions and options
- ✅ Toggle correct answers with one click
- ✅ Download extracted MCQs as JSON
- ✅ Clipboard copy functionality
- ✅ Toast notifications and progress tracking
- ✅ SQLite database for metadata persistence
- ✅ Responsive design (mobile & desktop)

---

## 🔗 Live Deployment Links

| Service | URL | Features |
|---------|-----|----------|
| **Frontend (GitHub Pages)** | https://saurabh7429.github.io/mcq-extractor-ai/ | Interactive UI hosted on GitHub |
| **Backend (Render)** | https://mcq-extractor-backend.onrender.com | Python Flask API on Render cloud |
| **GitHub Repository** | https://github.com/saurabh7429/MCQ-extractor-ai | Full source code & documentation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR APPLICATION                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   FRONTEND (GitHub Pages)                                   │
│   ────────────────────                                      │
│   • Location: github.io                                     │
│   • Files: index.html, preview.html                         │
│   • Purpose: User Interface                                 │
│   • Tech: HTML, CSS, JavaScript                             │
│                                                             │
│         │                                                   │
│         │ API Calls                                         │
         ▼                                                    │
│   BACKEND (Render.com)                                      │
│   ────────────────────                                      │
│   • Location: render.com (Cloud Server)                     │
│   • Files: backend/ folder                                  │
│   • Purpose: PDF Processing & AI Extraction                 │
│   • Tech: Python Flask, Gemini AI                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
MCQ-extractor-ai/
├── 📄 index.html              # Upload page (Frontend)
├── 📄 preview.html            # Preview page (Frontend)
├── 📁 js/                    # JavaScript files
│   ├── config.js             # API URL configuration
│   ├── upload.js            # Upload logic
│   └── preview.js           # Preview logic
├── 📁 css/
│   └── styles.css           # Styling
├── 📁 frontend/             # Copy of frontend files
├── 📁 backend/              # Flask API (Python)
│   ├── app.py              # Main Flask app
│   ├── config.py           # Configuration
│   ├── routes/             # API endpoints
│   │   ├── upload.py       # File upload
│   │   ├── extract.py      # MCQ extraction
│   │   └── download.py     # Download JSON
│   └── services/
│       ├── ai_processor.py # Gemini AI logic
│       ├── pdf_reader.py   # PDF reading
│       └── json_formatter.py
├── 📄 run.py               # Start local server
└── 📄 requirements.txt     # Python dependencies
```

---

## ⚙️ Configuration

### API URL (Where backend is connected)

**File:** `js/config.js` AND `frontend/js/config.js`

```javascript
API_BASE_URL: 'https://mcq-extractor-backend.onrender.com'
```

For **local testing**, change to:
```javascript
API_BASE_URL: 'http://localhost:5000'
```

---

## 🚀 How to Deploy

### Frontend → GitHub Pages
1. Push code to GitHub master branch
2. Go to Repository Settings → Pages
3. Select "master branch" as source
4. Save → Your site is live at `saurabh7429.github.io/mcq-extractor-ai/`

### Backend → Render.com
1. Connect GitHub to Render.com
2. Create Web Service
3. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`
4. Add Environment Variables:
   - `GEMINI_API_KEY` = your Google AI key
   - `SECRET_KEY` = random string

---

## 🧪 How to Test

### Method 1: Test on GitHub Pages (Production)
1. Open: https://saurabh7429.github.io/mcq-extractor-ai/
2. Upload any PDF file with MCQs
3. Click "Upload & Extract"
4. Wait for processing
5. View results on preview page

### Method 2: Test Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start server:
   ```bash
   python run.py
   ```
3. Open: http://localhost:5000
4. Upload PDF and test

### Test PDF Files
Place these in project root for testing:
- `testmcq.pdf` - First test file
- `testmcq1.pdf` - Second test file

---

## 🔧 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Failed to fetch" error | Check if Render backend is active |
| No MCQs extracted | Make sure PDF has text (not scanned image) |
| API Key error | Add GEMINI_API_KEY in Render env variables |
| CORS error | Backend on Render should allow all origins |

---

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Check if server is running |
| `/api/upload/file` | POST | Upload PDF file |
| `/api/extract/process` | POST | Extract MCQs from PDF |
| `/api/extract/preview` | POST | Get extracted MCQs |
| `/api/download/json` | POST | Download JSON file |

---

## Environment Variables

### 🔑 Required for Backend:

| Variable | Value | Where to Get |
|----------|-------|--------------|
| `GEMINI_API_KEY` | AI API key | https://aistudio.google.com/app/apikey |
| `SECRET_KEY` | Random string | Generate any random text |
| `FLASK_ENV` | production | Default |
| `RENDER` | 1 | Only on Render |

---

## 📞 Support

For issues:
1. Check Render backend logs
2. Verify GEMINI_API_KEY is set
3. Ensure PDF has selectable text and images
4. Check internet connection

---

**Last Updated:** March 2026
**Version:** 2.0.0
