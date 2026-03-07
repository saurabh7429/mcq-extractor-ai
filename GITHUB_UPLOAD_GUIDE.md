# GitHub & Render.com Par Deploy Guide (Hindi)

Is guide se aap apna MCQ Extractor AI website free me deploy kar payenge!

---

## Step 1: GitHub Account Create Karein

1. **Visit:** https://github.com
2. **Sign Up** button click karein
3. Email, password, username dal kar account create karein
4. Email verify karein

---

## Step 2: GitHub Desktop Install Karein (Recommended)

**Option A: GitHub Desktop (Easy)**

1. **Download:** https://desktop.github.com/
2. Install karein aur login karein apne GitHub account se

**Option B: Git Commands (Advanced)**

Agar aap git commands use karna chahte hain:

```bash
# Git install karne ke baad:
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## Step 3: Repository Create Karein

### GitHub Desktop Se:

1. GitHub Desktop open karein
2. **"Create a New Repository on Your Hard Drive"** click karein
3. Details fill karein:
   - **Name:** `MCQ-extractor-ai`
   - **Description:** "AI-powered MCQ Extractor from PDF"
   - **Local Path:** Jahan bhi aap chahein (e.g., `D:\my-projects\MCQ-extractor-ai`)
4. ✅ **"Keep this code private"** uncheck karein (public repo ke liye)
5. **"Create Repository"** click karein

### GitHub Website Se:

1. https://github.com/new open karein
2. Repository name: `MCQ-extractor-ai`
3. Public choose karein
4. **"Create repository"** click karein

---

## Step 4: Code Upload Karein

### GitHub Desktop Se:

1. Apna project folder open karein (jahan `run.py` hai)
2. GitHub Desktop automatically detect karega
3. **"Add an existing repository"** click karein
4. Apna folder select karein
5. **"Publish repository"** click karein

### Git Commands Se:

```bash
# Project folder me jayein
cd D:\your-folder\MCQ-extractor-ai

# Git init (agar nahi kiya)
git init

# Files add karein
git add .

# Commit karein
git commit -m "First upload - MCQ Extractor AI"

# Remote add karein (apni repo URL daleyn)
git remote add origin https://github.com/YOUR_USERNAME/MCQ-extractor-ai.git

# Push karein
git push -u origin main
```

---

## Step 5: Render.com Par Deploy Karein

### Create Account:

1. **Visit:** https://render.com
2. **"Sign Up"** click karein
3. **"GitHub"** se sign up karein
4. Authorize karein

### Create Web Service:

1. Dashboard me **"New +"** click karein
2. **"Web Service"** choose karein
3. Apni repository select karein (`MCQ-extractor-ai`)
4. Settings configure karein:

| Setting | Value |
|---------|-------|
| **Name** | `mcq-extractor-ai` |
| **Region** | Singapore (or closest to you) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python run.py` |

5. **"Advanced"** click karein
6. **"Add Environment Variables"** me ye add karein:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | `your-groq-api-key-here` |
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |
| `SECRET_KEY` | `any-random-string-like-abc123` |

### GROQ API Key Kahan Se Lein:

1. **Visit:** https://console.groq.com/keys
2. **"Create API Key"** click karein
3. Key copy karein
4. Render.com me `GROQ_API_KEY` variable me paste karein

### Deploy:

1. **"Create Web Service"** click karein
2. Wait karein (5-10 minutes)
3. Build complete hone ke baad URL milega (e.g., `https://mcq-extractor-ai.onrender.com`)

---

## Step 6: Website Test Karein

1. URL open karein
2. PDF upload karein
3. MCQs extract honge
4. Preview aur download kar payenge!

---

## Update Kaise Karein

Jab bhi code me changes karein:

### GitHub Desktop Se:

1. Changes auto dikhenge
2. **"Commit to main"** click karein
3. **"Push origin"** click karein
4. Render.com automatically update kar lega!

### Git Commands Se:

```bash
git add .
git commit -m "Updated code"
git push origin main
```

---

## Troubleshooting

### Build Fail Ho Raha Hai:

**Error:** `pip install -r requirements.txt` failed
- **Solution:** requirements.txt check karein, saare packages available hain?

### Website Load Nahi Ho Raha:

**Error:** Application Error
- **Solution:** Logs check karein - Environment variables sahi hain?

### API Error AA Raha Hai:

**Error:** "Please check your GROQ_API_KEY"
- **Solution:** 
  1. Render.com dashboard open karein
  2. Apni service click karein
  3. **"Environment"** tab me jahein
  4. `GROQ_API_KEY` verify karein
  5. Redeploy karein

### Slow Loading:

**Solution:**
- Region change karein (Singapore try karein)
- Free tier par 90 seconds idle ke baad sleep ho jata hai
- First request me thoda time lagega

---

## Important Security Notes

### ✅ DO:
- `.env` file ko GitHub par upload NA karein (already `.gitignore` me hai)
- API keys Sirf Render.com ke environment variables me rakhein
- Repository ko Public rakh sakte hain (API key secure rahegi)

### ❌ DON'T:
- API keys code me directly NA likhein
- `.env` file commit NA karein
- Sensitive files upload NA karein

---

## Free Tier Limits (Render.com)

| Feature | Free Tier |
|---------|----------|
| **Bandwidth** | 750 hours/month |
| **Sleep** | 15 min inactivity ke baad |
| **Build Time** | 500 minutes/month |
| **SSL** | ✅ Free |

---

## Summary

| Step | Action |
|------|--------|
| 1 | GitHub Account Create |
| 2 | GitHub Desktop Install |
| 3 | Repository Create & Upload |
| 4 | Render.com Setup |
| 5 | GROQ API Key Add |
| 6 | Deploy & Test |

---

## Koi Problem Ho To:

1. **Logs Check Karein:** Render.com dashboard > Service > Logs
2. **Redeploy Karein:** Dashboard > Manual Deploy > Clear build cache & deploy
3. **Environment Variables Verify Karein:** Service > Environment

---

## Contact

Koi bhi question ho toh pooch sakte hain!
