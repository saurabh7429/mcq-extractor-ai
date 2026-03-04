# MCQ-Extractor-AI Project Details

This document provides an overview of the **MCQ Extractor AI** project, including how the frontend and backend work, deployment platforms, and pros/cons of the architecture. It is meant to give a full picture for developers or stakeholders interested in the internals of the system.

---

## 📌 Project Summary

MCQ Extractor AI is a web application that allows users to upload PDF files containing multiple-choice questions (MCQs). The backend uses AI logic to extract the questions and options, stores them, and provides a preview and download interface to the user.

- Input: PDF file (max 10 MB).
- Output: JSON containing questions, options, and correct answers.
- Features: drag‑and‑drop upload, progress UI, inline editing & filtering of results, toast notifications, and file downloads.

## 🖥️ Frontend (GitHub)

The frontend is a **static single‑page UI** written in plain HTML, CSS, and vanilla JavaScript. There is no build step; the files live under `frontend/` and are suitable for hosting on any static hosting provider.

- **Hosting**: typically pushed to a GitHub repository and served via **GitHub Pages** or directly from the backend (Flask) when used together.
- **Structure**:
  - `index.html` – upload page with drag‑and‑drop area, file validation, and upload logic (`js/upload.js`).
  - `preview.html` – shows a grid of extracted MCQs (`js/preview.js`, `js/download.js`).
  - Shared CSS in `css/styles.css` for theming and responsive layout.
  - Utility JS (`js/status.js`) provides toast and loading components.
- **Interaction Flow**:
  1. User selects or drops a PDF, which is validated client‑side (type, size).
  2. File is uploaded via `fetch` to `/api/upload/file`.
  3. Upload response returns a `file_id`; extraction endpoint is called (`/api/extract/process`).
  4. Upon success, the file ID is stored in `sessionStorage` and the UI transitions to `preview.html`.
  5. Preview page fetches MCQ data from `/api/extract/preview` and renders cards.
  6. Users can filter/search, edit text inline, or change the marked correct answer.
  7. JSON can be copied to clipboard or downloaded (filtered or full).

- **Code highlights**:
  - `upload.js` handles drag events, file validation, and orchestrates the two API calls with loading states.
  - `preview.js` is responsible for rendering cards, search/filter logic, inline editing and marking correct answers, with local state tracking.
  - CSS variables and animations provide a modern UI feel.

- **Deployment (GitHub)**:
  - Push repository to GitHub, enable GitHub Pages with the `frontend/` directory as source or set up a workflow to build and deploy.
  - Alternatively, keep frontend in the same repository and serve it from the Flask backend (see backend section below). This way you can host both on a single domain.

### ✅ Pros

- Simple, framework‑free; easy to modify and debug.
- Works offline/off‑grid when files are already in user session (except upload/extract).
- Low hosting cost – static assets can be served for free via GitHub Pages.
- Complete control over UI without bundlers.

### ⚠️ Cons

- No component system; as UI grows, code may become harder to manage.
- No automatic bundling or minification – manual optimization needed for production.
- State is ephemeral (in-memory or sessionStorage); refreshing the page loses edits unless saved externally.
- Testing UI interactions requires manual or third‑party tools.

---

## ⚙️ Backend (Render.com)

The backend is a **Flask (Python) application** with the following characteristics:

- Entrypoint: `backend/app.py` defines `create_app()` factory.
- Configuration: `backend/config.py` loads environment variables to configure folders, database URL, logging, etc.
- Routes (blueprints) live in `backend/routes/`:
  - `upload.py` – handles `/api/upload/file` and `/api/upload/url`.
  - `extract.py` – orchestrates calling the AI service to parse PDFs (`/api/extract/process`), preview, and retrieve results.
  - `download.py` – serves JSON files by ID.
  - `validate.py` – miscellaneous checks (e.g., list of file IDs).
- Models and persistence in `backend/models/` using SQLite (local file) or an RDBMS defined by `DATABASE_URL`.
- Services (`backend/services/`) include:
  - `ai_processor.py` – contains logic to call the AI model or service (placeholder for GPT/Gemini etc.).
  - `pdf_reader.py` – reads and decompresses PDFs.
  - `json_formatter.py` – normalizes output to expected schema.
  - `storage_service.py` – manages files/JSON path.
- Utilities: validation, error handling, helpers.

### Deployment on Render.com

- The repo is connected to a Render web service. Upon push to main, Render installs dependencies from `requirements.txt` and runs a command such as `gunicorn backend.app:app`.
- Environment variables configure upload folder, secrets, and AI API keys.
- The frontend can be served as static assets by Flask (see `serve_index()` and `serve_static()` in `app.py`) or built separately and deployed via GitHub.

### Runtime Flow Summary

1. **File handling** – the uploaded PDF is saved in `UPLOAD_FOLDER`.
2. **Extraction** – `/api/extract/process` triggers `ai_processor.process_file()` which uses `pdf_reader` to parse then sends text to the AI model. Parsed MCQs are stored in a JSON file under `JSON_OUTPUT_FOLDER` and metadata is written to the database via `mcq_model.py`.
3. **Preview & Download** – associated endpoints read the JSON and return it to the frontend, or stream it for download.
4. **Health & static files** are also served by the Flask app.

### ✅ Pros

- Full backend control with Python; easy to extend and debug.
- Clean separation of concerns (routes, services, models).
- Works with Render’s free tier; the app can scale to moderate traffic.
- SQLite makes it zero‑config for small deployments, with ability to swap to PostgreSQL/MySQL by changing `DATABASE_URL`.
- Centralized logging with rotating files, helpful during development.

### ⚠️ Cons

- Using SQLite in production on Render may not persist across deploys; a managed database is recommended.
- Extracting large PDFs could be slow and may require background jobs or timeouts.
- No user authentication or rate‑limiting; open endpoints can be abused.
- The AI model integration is synchronous – long processing times block the request thread.

---

## 📂 Deployment Diagram

```mermaid
flowchart LR
    User-->|upload PDF|Frontend[Static UI (GitHub Pages)]
    Frontend-->|POST /api/upload/file|Backend[Flask App (Render.com)]
    Backend-->AI[AI Processor]
    AI-->JSON[Stored MCQs & DB]
    Frontend-->|preview/download|Backend
```

---

## 📝 Additional Notes

- **Testing**: there are unit tests under `tests/` for services and routes.
- **Environment**: requirements include Flask, SQLAlchemy, PyPDF2, and other libs in `requirements.txt`.
- **Configuration**: `.env.example` shows required vars (e.g. `DATABASE_URL`, `UPLOAD_FOLDER`).
- **Logs**: written to `backend/logs/app.log` with rolling behaviour.

---

This file should serve as a one‑stop reference for developers or reviewers wanting a clear understanding of how the project works, where each part is hosted, and what trade‑offs are present. You can copy, modify, or expand it as needed.
