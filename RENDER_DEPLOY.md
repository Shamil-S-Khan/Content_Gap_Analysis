# Render Deployment Guide

Deploy your Content Gap Analysis API and Dashboard to Render with **permanent free URLs**.

## What You Get

- ✅ **Permanent URLs** (never change)
- ✅ **Free tier** (no credit card needed)
- ✅ **Auto-deploy** from GitHub
- ✅ **HTTPS** included
- ✅ **Auto-restart** on crashes

Example URLs:
- API: `https://content-gap-api.onrender.com`
- Dashboard: `https://content-gap-dashboard.onrender.com`

---

## Quick Setup (3 steps)

### 1. Push Code to GitHub

```powershell
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/content-gap-analysis.git
git branch -M main
git push -u origin main
```

### 2. Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (easiest)
3. Authorize Render to access your repositories

### 3. Deploy Services

**Option A: One-Click Deploy (Recommended)**

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` and create both services automatically
5. Click **"Apply"**

**Option B: Manual Deploy**

Deploy API:
1. Click **"New +"** → **"Web Service"**
2. Connect repository: `content-gap-analysis`
3. Settings:
   - **Name:** `content-gap-api`
   - **Environment:** `Docker`
   - **Region:** `Oregon (US West)`
   - **Branch:** `main`
   - **Docker Command:** `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free`
4. Click **"Create Web Service"**

Deploy Dashboard:
1. Click **"New +"** → **"Web Service"**
2. Connect same repository
3. Settings:
   - **Name:** `content-gap-dashboard`
   - **Environment:** `Docker`
   - **Region:** `Oregon (US West)`
   - **Branch:** `main`
   - **Docker Command:** `python dashboard_app.py`
   - **Plan:** `Free`
4. Click **"Create Web Service"**

---

## After Deployment

### Get Your URLs

After deployment completes (~5-10 minutes):

**API URL:**
```
https://content-gap-api.onrender.com
```

**Dashboard URL:**
```
https://content-gap-dashboard.onrender.com
```

### Test API

```powershell
$API = "https://content-gap-api.onrender.com"

# Health check
Invoke-RestMethod "$API/health"

# Run analysis
$body = @{
    your_organization = "YourCompany"
    competitors = @("Competitor1")
} | ConvertTo-Json

Invoke-RestMethod -Method POST "$API/run" -Body $body -ContentType "application/json"

# Get recommendations
Invoke-RestMethod "$API/recommendations"

# Download PDF
Invoke-WebRequest "$API/download/pdf" -OutFile "report.pdf"
```

### Open Dashboard

Just visit your dashboard URL in a browser:
```
https://content-gap-dashboard.onrender.com
```

---

## Important Notes

### Free Tier Limitations

✅ **What's Included:**
- 750 hours/month (more than enough)
- Automatic HTTPS
- Continuous deployment
- Custom domains (optional)

⚠️ **Limitations:**
- **Spins down after 15 min inactivity** (first request takes ~30 seconds to wake up)
- 512 MB RAM
- Shared CPU

💡 **Pro Tip:** For 24/7 uptime, upgrade to paid plan ($7/month per service) or use a ping service to keep it awake.

### Keep Services Awake (Optional)

Use a free monitoring service to ping every 10 minutes:

**UptimeRobot** (free):
1. Sign up at https://uptimerobot.com
2. Add monitors for both URLs:
   - `https://content-gap-api.onrender.com/health`
   - `https://content-gap-dashboard.onrender.com`
3. Set interval to 5 minutes

This keeps services always ready (no cold starts).

---

## Auto-Deploy Updates

Once connected to GitHub, Render auto-deploys on every push:

```powershell
# Make changes to your code
git add .
git commit -m "Updated analysis logic"
git push

# Render automatically rebuilds and deploys (takes ~5 min)
```

Watch deployment progress at: https://dashboard.render.com

---

## Environment Variables

If you need to customize settings:

1. Go to https://dashboard.render.com
2. Select your service (API or Dashboard)
3. Go to **"Environment"** tab
4. Add variables:
   ```
   PYTHONUNBUFFERED=1
   DEBUG=False
   ```

---

## Troubleshooting

### Build Failed

Check build logs:
1. Go to https://dashboard.render.com
2. Click on your service
3. Go to **"Logs"** tab
4. Look for errors during build

Common fixes:
- Make sure `requirements.txt` is complete
- Check Dockerfile syntax
- Verify all files are committed to GitHub

### Service Not Responding

1. Check logs in Render dashboard
2. Verify health check endpoint: `curl https://your-service.onrender.com/health`
3. Service may be sleeping (free tier) - first request wakes it up (~30s)

### Port Issues

Render assigns dynamic ports via `$PORT` environment variable:
- API: Configured to use `$PORT` (handled by uvicorn)
- Dashboard: Updated to use `os.environ.get('PORT', 8050)`

---

## Monitoring

### View Logs

Real-time logs:
1. Go to https://dashboard.render.com
2. Select service
3. Click **"Logs"** tab
4. See live output

### Metrics

View service metrics:
1. Go to https://dashboard.render.com
2. Select service
3. Click **"Metrics"** tab
4. See CPU, memory, requests/sec

---

## Comparison: Render vs ngrok

| Feature | Render | ngrok |
|---------|--------|-------|
| **URL Permanence** | ✅ Permanent | ⚠️ Changes on restart (free) |
| **Custom Domain** | ✅ Free | 💰 Paid only |
| **Uptime** | ⚠️ Sleeps after 15min | ✅ Always on |
| **Setup** | Git push | Auth tokens |
| **HTTPS** | ✅ Automatic | ✅ Automatic |
| **Cost** | 100% Free | Free (1 tunnel) |
| **Best For** | Production | Development |

---

## Full Workflow

```powershell
# 1. Initial setup (one time)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/content-gap-analysis.git
git push -u origin main

# 2. Deploy on Render (web UI)
# - Go to render.com
# - Connect GitHub repo
# - Deploy blueprint (render.yaml)
# - Wait 5-10 minutes

# 3. Get your URLs
# API: https://content-gap-api.onrender.com
# Dashboard: https://content-gap-dashboard.onrender.com

# 4. Test
Invoke-RestMethod "https://content-gap-api.onrender.com/health"

# 5. Future updates
git add .
git commit -m "Updates"
git push
# Render auto-deploys in ~5 minutes
```

---

## Summary

✅ **Permanent URLs** - Never change  
✅ **Free** - No credit card needed  
✅ **Auto-deploy** - Push to GitHub = live in 5 min  
✅ **HTTPS** - Secure by default  
✅ **Professional** - Production-ready hosting  

Perfect for SPM project deployment! 🚀

---

## Alternative: Railway

If you prefer Railway over Render:

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Docker and deploys

Both work great - choose whichever you prefer!
