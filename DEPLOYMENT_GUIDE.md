# 🚀 CineGenie Deployment Guide

## Option 1: Render (Recommended - Easiest)

### Step 1: Prepare Your Code
1. Make sure all your files are committed to GitHub
2. Your project should have these files:
   - `render.yaml` ✅
   - `requirements.txt` ✅
   - `backend/app.py` ✅

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select your CineGenie repository
5. Render will auto-detect it's a Python app
6. Click "Create Web Service"

### Step 3: Set Environment Variables
In your Render dashboard, go to "Environment" tab and add:
```
TMDB_API_KEY=your_tmdb_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Step 4: Deploy
- Click "Deploy" and wait 5-10 minutes
- Your app will be live at: `https://your-app-name.onrender.com`

---

## Option 2: Railway (Alternative)

### Step 1: Deploy to Railway
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your CineGenie repository
4. Railway will auto-detect Python

### Step 2: Set Environment Variables
In Railway dashboard, add:
```
TMDB_API_KEY=your_tmdb_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Step 3: Deploy
- Railway will automatically deploy
- Your app will be live at: `https://your-app-name.railway.app`

---

## Option 3: Heroku (Legacy - Requires Credit Card)

### Step 1: Install Heroku CLI
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Deploy
```bash
heroku create your-cinegenie-app
git push heroku main
```

### Step 3: Set Environment Variables
```bash
heroku config:set TMDB_API_KEY=your_tmdb_api_key_here
heroku config:set GOOGLE_API_KEY=your_google_api_key_here
```

---

## 🎯 Recommended: Render

**Why Render?**
- ✅ Free tier available
- ✅ No credit card required
- ✅ Auto-deploys from GitHub
- ✅ Easy environment variable setup
- ✅ Perfect for Flask apps

**Steps:**
1. Push your code to GitHub
2. Sign up at render.com
3. Connect your repo
4. Add your API keys
5. Deploy!

Your app will be live in 10 minutes! 🎉

---

## 🔧 Troubleshooting

### If deployment fails:
1. Check the logs in your hosting platform
2. Make sure all files are committed to GitHub
3. Verify your API keys are set correctly
4. Check that `requirements.txt` has all dependencies

### Common issues:
- **Port binding**: Fixed in `render.yaml`
- **Missing dependencies**: Updated `requirements.txt`
- **Environment variables**: Make sure to set them in the dashboard

---

## 📱 Your Live App

Once deployed, your CineGenie will be available at:
- **Render**: `https://your-app-name.onrender.com`
- **Railway**: `https://your-app-name.railway.app`
- **Heroku**: `https://your-app-name.herokuapp.com`

Share this URL with friends to show off your movie recommendation app! 🎬 