# 🚀 Deploy to Render - Quick Checklist

## ✅ Files Ready

You have all the necessary files:
- ✅ `render.yaml` - Deployment configuration
- ✅ `Dockerfile` - Container definition (updated for Render)
- ✅ `dashboard_app.py` - Updated to use PORT env var
- ✅ `requirements.txt` - Python dependencies
- ✅ All application code

## 📋 Deployment Steps

### Step 1: Push to GitHub (5 minutes)

```powershell
# Make sure you're in the project directory
cd C:\Fast_Nukes_Universiry\Semester_7\SPM\SPM_Project\content_gap_analysis

# Initialize git (if not already done)
git init
git add .
git commit -m "Deploy to Render"

# Create a new repo on GitHub: https://github.com/new
# Name it: content-gap-analysis

# Then push:
git remote add origin https://github.com/YOUR_USERNAME/content-gap-analysis.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render (2 minutes)

1. **Go to:** https://render.com
2. **Sign up** with GitHub (click "Get Started for Free")
3. **Authorize** Render to access your repositories
4. **Click:** "New +" → "Blueprint"
5. **Select:** your `content-gap-analysis` repository
6. **Click:** "Apply" (Render reads `render.yaml` automatically)

### Step 3: Wait for Build (~10 minutes)

Render will:
- ✅ Build Docker image (5-7 minutes)
- ✅ Deploy API service
- ✅ Deploy Dashboard service
- ✅ Assign permanent URLs

### Step 4: Get Your URLs

After deployment:

**API:**
```
https://content-gap-api.onrender.com
```

**Dashboard:**
```
https://content-gap-dashboard.onrender.com
```

(URLs will be shown in Render dashboard)

### Step 5: Test

```powershell
# Replace with your actual URL from Render
$API = "https://content-gap-api.onrender.com"

# Health check (may take 30s on first request - service waking up)
Invoke-RestMethod "$API/health"

# Run analysis
$body = @{} | ConvertTo-Json
Invoke-RestMethod -Method POST "$API/run" -Body $body -ContentType "application/json"
```

## 🎯 Expected Results

**API Service:**
- Name: `content-gap-api`
- Status: `Live` (green)
- URL: `https://content-gap-api.onrender.com`
- Health: `https://content-gap-api.onrender.com/health`

**Dashboard Service:**
- Name: `content-gap-dashboard`
- Status: `Live` (green)
- URL: `https://content-gap-dashboard.onrender.com`

## ⚡ Tips

### Keep Services Awake

Free tier sleeps after 15 min. To keep awake:

1. **UptimeRobot** (free monitoring):
   - Go to https://uptimerobot.com
   - Create monitor for: `https://content-gap-api.onrender.com/health`
   - Interval: 5 minutes
   - This pings your service to keep it awake

### View Logs

1. Go to https://dashboard.render.com
2. Click on your service
3. Click "Logs" tab
4. See real-time output

### Redeploy

Option A - Auto (recommended):
```powershell
git add .
git commit -m "Update"
git push
# Render auto-deploys in ~5 min
```

Option B - Manual:
1. Go to Render dashboard
2. Click service
3. Click "Manual Deploy" → "Deploy latest commit"

## 🐛 Troubleshooting

### Build Failed
- Check logs in Render dashboard
- Make sure all files are committed to GitHub
- Verify `requirements.txt` has all dependencies

### Service Won't Start
- Check logs for Python errors
- Make sure `PORT` variable is used (already configured)
- Try manual deploy

### Slow First Request
- Normal! Free tier sleeps after 15 min
- First request wakes it up (~30 seconds)
- Subsequent requests are fast

## 📊 What's Deployed

Both services run the same Docker image with different commands:

**API (Port 10000):**
```bash
uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

**Dashboard (Port 10000):**
```bash
python dashboard_app.py
```

## ✨ Benefits vs ngrok

| Feature | Render | ngrok |
|---------|--------|-------|
| URL Changes | ❌ Never | ✅ Every restart |
| Credit Card | ❌ Not needed | ❌ Not needed |
| Setup Time | 15 min | 2 min |
| Production Ready | ✅ Yes | ⚠️ Dev only |
| Auto-deploy | ✅ Git push | ❌ Manual |
| Custom Domain | ✅ Free | 💰 $8/month |

## 🎓 For SPM Project

Perfect for your project because:
- ✅ **Professional** - Real production hosting
- ✅ **Permanent URLs** - Never change
- ✅ **Free** - No cost
- ✅ **Auto-deploy** - Push code = live
- ✅ **HTTPS** - Secure
- ✅ **Logs & Monitoring** - Built-in

## 📝 Summary

```
1. Push to GitHub (5 min)
2. Deploy on Render (2 min)
3. Wait for build (10 min)
4. Get permanent URLs
5. Test and share!
```

Total time: **~20 minutes** for permanent, professional hosting! 🚀
