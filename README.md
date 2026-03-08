# 🤖 MCQ Extractor AI

### Turn Your PDF Questions into Digital MCQs in Seconds!

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-GROQ-purple?style=for-the-badge)
![Live](https://img.shields.io/badge/Live-Render-brightgreen?style=for-the-badge)

---

## ✨ What Does This Do?

Ever had a PDF with 100+ MCQs and wished you had them in a digital format? 

**MCQ Extractor AI** does exactly that! 
- Upload a PDF 📄
- AI reads and extracts all questions 🎯
- Get JSON with questions, options & correct answers 📝
- Download or preview instantly 🚀

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
| 💾 **JSON Export** | Download MCQs in standard JSON format |
| 🔒 **Secure** | Your files stay on server, deleted after processing |

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
│   HTML5  •  CSS3  •  JavaScript (Vanilla)         │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    BACKEND                          │
│   Python  •  Flask  •  GROQ API (Llama 3.1)       │
└─────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
     ┌─────────┐    ┌──────────┐    ┌──────────┐
     │  pypdf  │    │  SQLite  │    │ gunicorn │
     │ (Reader)│    │    DB    │    │  Server  │
     └─────────┘    └──────────┘    └──────────┘
```

---

## 📸 How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Upload    │────►│    AI       │────►│  Download   │
│     PDF     │     │  Processes  │     │     JSON    │
└─────────────┘     └─────────────┘     └─────────────┘
     1 click          5-30 sec            Done!
```

### Step-by-Step:
1. **Drop your PDF** - Drag & drop or click to upload
2. **AI Magic** - Llama 3.1 reads and extracts questions
3. **Preview** - See all MCQs on screen
4. **Download** - Get JSON file instantly

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
├── 🖥️  frontend/          # Web UI (HTML/CSS/JS)
│   ├── index.html         # Upload page
│   ├── preview.html      # Results page
│   ├── css/styles.css    # Beautiful styling
│   └── js/               # Client-side scripts
│
├── ⚙️   backend/          # Server (Python/Flask)
│   ├── app.py            # Main Flask app
│   ├── routes/           # API endpoints
│   │   ├── upload.py     # Handle file upload
│   │   ├── extract.py    # MCQ extraction
│   │   └── download.py   # JSON download
│   ├── services/          # Core logic
│   │   ├── ai_processor.py    # GROQ AI integration
│   │   ├── pdf_reader.py      # PDF text extraction
│   │   └── json_formatter.py  # Format output
│   └── models/           # Database
│
├── 💾  storage/           # File storage
│   ├── uploaded_pdfs/     # Uploaded PDFs
│   └── generated_json/   # Output JSON files
│
├── 📊  database/          # SQLite database
├── 📝  requirements.txt   # Python packages
└── 🚀  render.yaml       # Deploy config
```

---

## 🔑 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/file` | POST | Upload PDF |
| `/api/extract/<file_id>` | POST | Extract MCQs |
| `/api/download/<filename>` | GET | Download JSON |
| `/api/health` | GET | Server health check |

---

## 🌐 Deployment

### Deploy to Render (Free!)

1. **Push to GitHub**
```bash
git add .
git commit -m "Ready to deploy"
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

## ❓ FAQ

**Q: Is it free?**
> Yes! GROQ provides free tier with generous limits. No credit card needed.

**Q: What PDFs work?**
> Text-based PDFs (not scanned images). If you can select text in PDF, it will work!

**Q: Where are files stored?**
> Files are stored temporarily and deleted after processing. Nothing is kept permanently.

**Q: Can I use on mobile?**
> Absolutely! The UI is fully responsive.

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


