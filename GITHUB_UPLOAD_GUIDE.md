# GitHub Par Code Upload Guide (GUI Se)

## Step 1: GitHub Desktop Install Karein

1. **Download GitHub Desktop:**
   - Visit: https://desktop.github.com/
   - Click "Download for Windows"

2. **Install Karein:**
   - Open the downloaded file
   - Follow installation steps
   - Login with your GitHub account when prompted

---

## Step 2: Repository Create Karein

1. **GitHub Desktop Open Karein**
2. **Click: "Create a New Repository on Your Hard Drive"**
   - Name: `MCQ-extractor-ai`
   - Description: "AI-powered MCQ Extractor from PDF"
   - Local Path: `D:\usb_A\workspace\MCQ-extractor-ai` (Select your folder)
   - ✅ "Keep this code private" (Agar private repo chahiye)
   - ❌ "Keep this code private" (Agar public repo chahiye - website ke liye)
   - Click "Create Repository"

---

## Step 3: Code Commit Karein

1. **GitHub Desktop Me Dekhenge:**
   - Niche "Changes" tab pe click Karein
   - Upar files dikhengi jo changed hain

2. **Summary Me Likhein:**
   - First upload - Initial commit

3. **"Commit to main" Button Click Karein**

---

## Step 4: GitHub Par Push Karein

1. **"Publish repository" Button Click Karein**
   - Ye button upar right side pe hoga

2. **Settings:**
   - ✅ "Keep this code private" (Private repo ke liye)
   - ❌ "Keep this code private" (Public repo ke liye)
   - Click "Publish Repository"

---

## Step 5: Website Live Karein (Public Repo Ke Liye)

**Option A: Vercel Se (Free & Easy)**

1. Visit: https://vercel.com
2. Sign up with GitHub
3. Click "Add New Project"
4. Select your repository: `MCQ-extractor-ai`
5. Framework Preset: Other
6. Build Command: Leave blank
7. Output Directory: `frontend`
8. Click "Deploy"

**Option B: Render Se**

1. Visit: https://render.com
2. Sign up with GitHub
3. Click "New Web Service"
4. Connect your GitHub repo
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python run.py`

---

## API Secure Kaise Karein

### Method 1: Environment Variables (Recommended)

1. **Vercel/Render Me:**
   - Dashboard me jahein
   - "Environment Variables" section me jahein
   - Add karein:
     - `GEMINI_API_KEY` = your-api-key
     - `SECRET_KEY` = random-string

2. **Code Me Changes:**
   - File: `backend/config.py` - Already .env se load karta hai ✅

### Method 2: API Rate Limiting

Add rate limiting to prevent abuse:

```
python
# backend/utils/rate_limiter.py (Naya file)
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## Important Security Notes

### ✅ Do:
- `.env` file ko kabhi GitHub par upload na karein
- `.gitignore` file use karein (Pehle se added hai)
- API keys ko environment variables me store karein
- Private repo use karein agar sensitive data hai

### ❌ Don't:
- API keys directly code me na likhein
- `.env` file ko commit na karein
- Public repo me sensitive files na upload karein

---

## Troubleshooting

### "Permission Denied" Error:
- GitHub Desktop me Login check karein
- Repository settings me jahein

### "File Too Large" Error:
- Large files (10MB+) GitHub par nahi chalte
- Use `.gitignore` - Already added hai storage folder ke liye

### Website Not Loading:
- Build logs check karein
- Output directory: `frontend` set karein

---

## Summary

| Step | Action |
|------|--------|
| 1 | GitHub Desktop Install Karein |
| 2 | Repository Create Karein |
| 3 | Code Commit Karein |
| 4 | Publish to GitHub |
| 5 | Vercel/Render par Deploy Karein |
| 6 | Environment Variables Set Karein |

---

## Next Steps

1. GitHub Desktop download karein
2. Repository create karein
3. Code push karein
4. Deployment platform par deploy karein
5. API key add karein

Koi bhi question ho toh pooch sakte hain!
