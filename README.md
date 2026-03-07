# MCQ Extractor AI 🤖📝

AI-powered tool to extract MCQs from PDF files using Gemini AI.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- 📄 **PDF to MCQ Conversion** - Extract multiple choice questions from PDF files
- 🤖 **AI-Powered** - Uses Google Gemini AI for intelligent extraction
- 🎯 **High Accuracy** - Precise question, options, and answer extraction
- 🌐 **Web Interface** - User-friendly frontend for easy interaction
- 📊 **Database Storage** - SQLite database for storing MCQs
- 🔒 **Secure** - Environment-based API key management

## Demo

[Add your deployed website URL here]

## Tech Stack

- **Backend:** Python, Flask
- **AI:** Google Gemini API
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **PDF Processing:** PyPDF2, pdfplumber

## Getting Started

### Prerequisites

- Python 3.10 or higher
- GitHub Account
- Gemini API Key (Free from https://aistudio.google.com/app/apikey)

### Installation

1. **Clone the repository:**
   
```
bash
   git clone https://github.com/YOUR_USERNAME/MCQ-extractor-ai.git
   cd MCQ-extractor-ai
   
```

2. **Create virtual environment:**
   
```
bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   
```

3. **Install dependencies:**
   
```
bash
   pip install -r requirements.txt
   
```

4. **Setup environment variables:**
   
```
bash
   copy .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   
```

5. **Run the application:**
   
```
bash
   python run.py
   
```

6. **Open in browser:**
   
```
   http://localhost:5000
   
```

## Usage

1. Open the web interface
2. Click on the upload area or drag & drop a PDF file
3. Click "Upload & Extract" button
4. Wait for AI processing
5. Preview and download your MCQs in JSON format

## Project Structure

```
MCQ-extractor-ai/
├── backend/
│   ├── app.py              # Flask application
│   ├── config.py           # Configuration
│   ├── routes/             # API routes
│   │   ├── upload.py       # File upload
│   │   ├── extract.py      # MCQ extraction
│   │   └── download.py     # File download
│   ├── services/           # Business logic
│   ├── models/             # Database models
│   └── utils/              # Utilities
├── frontend/
│   ├── index.html          # Main page
│   ├── preview.html        # Preview page
│   ├── css/                # Styles
│   └── js/                 # Frontend scripts
├── storage/                # File storage
├── database/               # SQLite database
├── logs/                   # Application logs
├── requirements.txt        # Python dependencies
└── run.py                  # Entry point
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/file` | POST | Upload PDF file |
| `/api/extract/<file_id>` | GET | Extract MCQs from file |
| `/api/download/<file_id>` | GET | Download JSON file |
| `/api/health` | GET | Health check |

## Deployment

### Deploy to Vercel (Frontend + API)

1. Push code to GitHub
2. Go to https://vercel.com
3. Import your repository
4. Set environment variables:
   - `GEMINI_API_KEY` = your-api-key
   - `SECRET_KEY` = random-string
5. Deploy!

### Deploy to Render

1. Push code to GitHub
2. Go to https://render.com
3. Create new Web Service
4. Connect GitHub repo
5. Set environment variables
6. Deploy!

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API Key | Yes |
| `SECRET_KEY` | Flask secret key | No |
| `FLASK_ENV` | production/development | No |
| `LOG_LEVEL` | INFO/DEBUG | No |

## Security

- ✅ API keys stored in environment variables
- ✅ .env file in .gitignore (never uploaded)
- ✅ File type validation
- ✅ File size limits (10MB max)
- ✅ Secure filename handling

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- [Google Gemini AI](https://gemini.google.com/)
- [Flask](https://flask.palletsprojects.com/)
- [PyPDF2](https://pypdf2.readthedocs.io/)

---

Made with ❤️ for education
