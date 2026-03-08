# 🤖 MCQ Extractor AI

### Turn Your PDF Questions into Digital MCQs in Seconds!

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-GROQ-purple?style=for-the-badge)
![Live](https://img.shields.io/badge/Live-Render-brightgreen?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.4.0-blue?style=for-the-badge)

---

## ✨ What Does This Do?

Ever had a PDF with 100+ MCQs and wished you had them in a digital format? 

**MCQ Extractor AI** does exactly that! 
- Upload a PDF 📄
- AI reads and extracts all questions 🎯
- Get JSON with questions, options & correct answers 📝
- Download in multiple formats or print directly 🚀

---

## 🎯 Live Demo

**Try it now:** 👉 [https://mcq-extractor-ai.onrender.com](https://mcq-extractor-ai.onrender.com)

*(Works on mobile too!)*

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered** | Uses GROQ's Llama 3.1 model for smart extraction |
| 📄 **PDF Support** | Extract from text-based PDFs |
| 🎯 **Accurate** | Gets questions, 4 options & correct answers |
| 🌐 **Web Based** | No installation needed - runs in browser |
| 💾 **Multiple Formats** | Export to JSON, CSV, Excel, DOCX & more |
| 🖨️ **Print-Ready** | Direct PDF export for printing |
| 📝 **DOCX Export** | Word document for question papers |
| 🔒 **Secure** | Your files stay on server, deleted after processing |

### Export Formats Available:

**Digital Formats (Export As):**
- JSON, CSV, TXT, Markdown, HTML, XML, YAML
- SQL (database insert statements)
- Aiken & GIFT (Moodle import formats)
- Excel (XLSX)

**Print-Ready Formats (Print Formats):**
- Question Paper PDF
- Answer Key PDF
- OMR Sheet PDF (for bubble answer sheets)
- Tabular PDF (table format)
- DOCX Question Paper (Word document)

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND                               │
│   HTML5  •  CSS3  •  JavaScript (Vanilla)                 │
│   Bootstrap  •  Responsive Design                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND                                 │
│   Python  •  Flask  •  GROQ API (Llama 3.1 8B)          │
└─────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
     ┌─────────┐    ┌──────────┐    ┌──────────┐
     │  pypdf  │    │  SQLite  │    │ gunicorn │
     │ (Reader)│    │    DB    │    │  Server  │
     └─────────┘    └──────────┘    └──────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ reportlab │   │python-docx│   │ openpyxl  │
    │ (PDF Gen) │   │(DOCX Gen) │   │(Excel Gen)│
    └───────────┘   └───────────┘   └───────────┘
```

---

## 📸 How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Upload    │────►│     AI      │────►│   Preview   │
│     PDF     │     │  Processes  │     │  & Download │
└─────────────┘     └─────────────┘     └─────────────┘
     1 click          5-30 sec            Done!
```

### Step-by-Step Detailed Workflow:

**Step 1: Upload PDF**
- User drags/drops or clicks to upload PDF
- Browser sends file to `/api/upload/file`
- Backend validates file (type, size)
- Generates unique UUID for the file
- Saves PDF to `storage/uploaded_pdfs/`

**Step 2: AI Processing**
- Backend reads PDF text using pypdf
- Sends text to GROQ API (Llama 3.1 8B model)
- AI extracts MCQs with proper structure
- Returns raw MCQ data in JSON format

**Step 3: Data Formatting**
- JSON Formatter validates and cleans data
- Ensures each question has exactly 4 options
- Sets correct_answer as index (0-3)
- Removes duplicates and invalid entries

**Step 4: Storage & Response**
- Saves formatted JSON to `storage/generated_json/`
- Returns MCQs to frontend
- Frontend displays preview cards

**Step 5: Export Options**
- Multiple digital formats (JSON, CSV, etc.)
- Print-ready formats (PDF, DOCX)
- One-click download

---

## 🏃‍♂️ Quick Start (Local)

```bash
# 1. Clone the repo
git clone https://github.com/saurabh7429/mcq-extractor-ai.git
cd mcq-extractor-ai

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Windows)
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup API key
copy .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here
# Get free key: https://console.groq.com/keys

# 6. Run!
python run.py

# 7. Open browser
http://localhost:5000
```

---

## 📁 Project Structure

```
mcq-extractor-ai/
│
├── 🖥️  frontend/              # Web UI (HTML/CSS/JS)
│   ├── index.html             # Upload page
│   ├── preview.html           # Results page with export options
│   ├── css/styles.css         # Beautiful styling
│   └── js/                   # Client-side scripts
│       ├── upload.js         # File upload handling
│       ├── preview.js         # MCQ display & export
│       ├── status.js         # Status messages
│       └── download.js       # Download functionality
│
├── ⚙️   backend/              # Server (Python/Flask)
│   ├── app.py                # Main Flask application
│   ├── config.py             # Configuration settings
│   ├── routes/               # API endpoints
│   │   ├── upload.py         # POST /api/upload/file
│   │   ├── extract.py        # POST /api/extract/<file_id>
│   │   ├── download.py       # GET /api/download/*
│   │   └── validate.py       # POST /api/validate
│   ├── services/             # Core business logic
│   │   ├── ai_processor.py      # GROQ AI integration
│   │   ├── pdf_reader.py         # PDF text extraction
│   │   ├── json_formatter.py    # Format & validate MCQs
│   │   ├── export_service.py    # Export to all formats ⭐NEW
│   │   └── storage_service.py   # File I/O operations
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
│   ├── uploaded_pdfs/        # Uploaded PDFs
│   └── generated_json/        # Output JSON files
│
├── 📊  database/             # SQLite database
├── 📝  requirements.txt       # Python packages
├── 🚀  run.py               # Application entry point
├── 🔧  render.yaml          # Render deployment config
└── 📚  PROJECT_DOC.md       # Detailed documentation
```

---

## 🔑 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/file` | POST | Upload PDF file |
| `/api/extract/<file_id>` | POST | Extract MCQs from PDF |
| `/api/download/<file_id>` | GET | Download original JSON |
| `/api/download/export/<format>/<file_id>` | GET | Export in specified format ⭐NEW |
| `/api/download/list` | GET | List all files |
| `/api/download/export/formats` | GET | Get supported formats |
| `/api/health` | GET | Server health check |

### New Export Formats:
```
/api/download/export/question_pdf/<file_id>     # Question Paper PDF
/api/download/export/answer_key_pdf/<file_id>   # Answer Key PDF
/api/download/export/omr_pdf/<file_id>          # OMR Sheet PDF
/api/download/export/tabular_pdf/<file_id>      # Tabular PDF
/api/download/export/docx/<file_id>              # DOCX Question Paper
```

---

## 🌐 Deployment

### Deploy to Render (Free!)

1. **Push to GitHub**
```bash
git add .
git commit -m "v2.4.0 - Added print-ready export formats"
git push origin main
```

2. **Go to [render.com](https://render.com)**
- New → Web Service
- Connect your GitHub repo
- Configure:
  - Build: `pip install -r requirements.txt`
  - Start: `gunicorn backend.app:app --workers 4 --bind 0.0.0.0:$PORT`

3. **Add Environment Variable:**
- `GROQ_API_KEY` = your key from https://console.groq.com/keys

4. **Done!** 🎉 Your app is live!

---

## 📊 What's New in v2.4.0

### Added Print-Ready Export Formats:
- ✅ Question Paper PDF (print without answers)
- ✅ Answer Key PDF (teachers copy)
- ✅ OMR Sheet PDF (bubble answer sheets)
- ✅ Tabular PDF (table format)
- ✅ DOCX Question Paper (Word document)

### Added Button Functionality:
- ✅ Copy JSON button
- ✅ Download JSON button
- ✅ Print Formats dropdown (separate from Export As)
- ✅ Fixed button click handlers

### Updated Documentation:
- ✅ PROJECT_DOC.md - Full details with export formats
- ✅ DEPLOY.md - New dependencies info

---

## ❓ FAQ

**Q: Is it free?**
> Yes! GROQ provides free tier with generous limits. No credit card needed.

**Q: What PDFs work?**
> Text-based PDFs (not scanned images). If you can select text in PDF, it will work!

**Q: Where are files stored?**
> Files are stored temporarily and deleted after processing. Nothing is kept permanently.

**Q: Can I use on mobile?**
> Absolutely! The UI is fully responsive.

**Q: What new export formats are available?**
> You can now export to Question Paper PDF, Answer Key PDF, OMR Sheet PDF, Tabular PDF, and DOCX!

**Q: How much memory does it use?**
> Optimized for Render free tier (512MB). Uses lightweight libraries (~7MB total).

---

## 🤝 Contributing

Found a bug? Have a feature idea?

1. Fork the repo
2. Create your feature branch
3. Make changes and test
4. Submit a Pull Request

---

## 📜 License

MIT License - Free to use, modify, and distribute!

---

## ⭐ Show Support

If this project helped you, give it a ⭐ on GitHub!

---

## 🔗 Quick Links

- **Live App:** https://mcq-extractor-ai.onrender.com
- **GROQ API:** https://console.groq.com/keys
- **Render Deploy:** https://render.com

---

<div align="center">

Made with ❤️ using Flask + GROQ AI

*Turn boring PDFs into awesome digital quizzes!* 🎉

</div>

