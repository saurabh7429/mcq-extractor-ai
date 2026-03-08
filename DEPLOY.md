# MCQ Extractor AI - Deployment Guide

## Important Note
**GitHub Pages cannot host Python/Flask backends.** It only serves static files. For a full-stack Flask app like this, you need **Render.com** (or similar) for the backend.

## Deployment Options

### Option 1: Full Deploy on Render (Recommended) ✅
Deploy both frontend + backend on Render - simplest approach

---

## Option 1: Deploy Everything on Render

### Steps:

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com) → Sign in with GitHub
   - Click "New" → "Web Service"
   - Select your repository `mcq-extractor-ai`
   - Configure:
     - **Name:** mcq-extractor-ai
     - **Environment:** Python
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn backend.app:app --workers 4 --bind 0.0.0.0:$PORT`
   - Add Environment Variable:
     - `GROQ_API_KEY` = your Groq API key (see below)
   - Click "Create Web Service"

3. **Wait for deployment** (2-5 minutes)

4. **Your app is live!** URL: `https://mcq-extractor-ai.onrender.com`

---

## Where to Store GROQ_API_KEY?

**You store your API key in ONE place only:**

### In Render Dashboard (Production):
When you create the web service on Render, add the environment variable:
- Key: `GROQ_API_KEY`
- Value: `gsk_xxxxxxxxxxxxxxxxxxxx` (your actual key from Groq)

**Do NOT add it to .env file or GitHub** - keep it secure in Render!

### In .env file (Local Development only):
For local testing, create a `.env` file in project root:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

---

## Getting GROQ API Key:

1. Go to [groq.com](https://console.groq.com/keys)
2. Click "Create API Key"
3. Copy the key
4. Add it to Render Dashboard

**Note:** GROQ provides free tier with generous limits!

---

## Troubleshooting

### "Application failed to start"
- Check if `GROQ_API_KEY` is set in Render dashboard
- Check build logs in Render

### "No GROQ_API_KEY found"
- The app will still work but use mock data (demo MCQs)
- Add your key in Render Dashboard → Environment Variables

### "Database error"
- The app automatically uses `/tmp` for database on Render (configured in config.py)

### "CORS error"
- CORS is already configured in app.py for all origins

---

## Files Created for Deployment

- `render.yaml` - Render configuration (auto-deploy)
- `.env.example` - Template for environment variables

## Files NOT to commit:
- `.env` - Contains API keys (add to .gitignore)
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python
- `logs/` - Log files
- `storage/` - Uploaded files

