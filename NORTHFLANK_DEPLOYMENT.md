# Northflank Deployment Guide

Deploy Content Gap Analysis on Northflank's free tier.

---

## Why Northflank?

- ✅ **Free tier** - 2 services, 512MB RAM each
- ✅ **Auto HTTPS** - Free SSL certificates
- ✅ **CI/CD** - Auto-deploy from GitHub
- ✅ **Public URLs** - No ngrok needed

---

## Deployment Steps

### Step 1: Create API Service

1. Go to https://app.northflank.com
2. Click **"Create Service"** → **"Combined"** (Build and Deploy)
3. Configure:
   - **Service name**: `content-gap-api`
   - **Repository**: `Shamil-S-Khan/Content_Gap_Analysis`
   - **Branch**: `master`
   - **Build type**: `Dockerfile`
   - **Build context**: `/`
   - **Dockerfile location**: `/Dockerfile`
   - **BuildKit**: Enabled (suggested)

4. **Resources**:
   - **Compute plan**: `nf-compute-20` (0.2 vCPU, 512 MB) - FREE
   - **Instances**: 1

5. **Networking** - Add Port:
   - **Port**: `8000`
   - **Protocol**: `HTTP`
   - **Publicly expose**: ✅ Enabled
   - **Name**: `api`
   
   Your API will be at: `https://api--content-gap-api--PROJECT.code.run`

6. Click **"Create Service"**

---

### Step 2: Create Dashboard Service

1. Click **"Create Service"** → **"Combined"**
2. Configure:
   - **Service name**: `content-gap-dashboard`
   - **Repository**: `Shamil-S-Khan/Content_Gap_Analysis`
   - **Branch**: `master`
   - **Build type**: `Dockerfile`
   - **Build context**: `/`
   - **Dockerfile location**: `/Dockerfile`

3. **Resources**:
   - **Compute plan**: `nf-compute-20` (FREE)
   - **Instances**: 1

4. **Networking** - Add Port:
   - **Port**: `8050`
   - **Protocol**: `HTTP`
   - **Publicly expose**: ✅ Enabled
   - **Name**: `dashboard`

5. **Environment Variables**:
   - **Name**: `API_URL`
   - **Value**: `http://content-gap-api:8000` (internal service communication)

6. **Advanced** → **Docker runtime mode**:
   - Select **"Custom command"**
   - **Command**: `python dashboard.py`

7. Click **"Create Service"**

---

## Access Your Services

After deployment (takes 3-5 minutes):

- **API**: `https://api--content-gap-api--[PROJECT].code.run`
- **Dashboard**: `https://dashboard--content-gap-dashboard--[PROJECT].code.run`
- **API Docs**: `https://api--content-gap-api--[PROJECT].code.run/docs`

Replace `[PROJECT]` with your actual project ID from Northflank.

---

## Test Deployment

```bash
# Test API health
curl https://api--content-gap-api--[PROJECT].code.run/health

# Run analysis
curl -X POST https://api--content-gap-api--[PROJECT].code.run/run \
  -H "Content-Type: application/json" \
  -d '{
    "competitor_url": "https://example.com/article1",
    "target_url": "https://example.com/article2"
  }'
```

---

## Auto-Deploy on Git Push

✅ **Already configured!** Every push to `master` branch automatically:
1. Builds new Docker image
2. Deploys to Northflank
3. Runs health checks
4. Switches traffic to new version

---

## View Logs

1. Go to your service in Northflank dashboard
2. Click **"Logs"** tab
3. Real-time logs appear

Or use CLI:
```bash
# Install Northflank CLI
npm install -g @northflank/cli

# Login
northflank login

# View logs
northflank logs service content-gap-api
northflank logs service content-gap-dashboard
```

---

## Free Tier Limits

| Resource | Free Tier | Your Usage |
|----------|-----------|------------|
| Services | 2 | 2 (API + Dashboard) |
| vCPU | 0.2 shared per service | 0.4 total |
| RAM | 512 MB per service | 1 GB total |
| Build time | Unlimited | ~2 min per deploy |
| Bandwidth | Fair use | Minimal |

**Cost: $0/month** ✅

---

## Troubleshooting

### Service won't start?
- Check logs in Northflank dashboard
- Verify Dockerfile builds locally: `docker build -t test .`
- Check port configuration (8000 for API, 8050 for Dashboard)

### Dashboard can't reach API?
- Verify `API_URL` environment variable is set to `http://content-gap-api:8000`
- Services must be in same project to communicate

### Out of memory?
- 512MB should be enough for each service
- If issues, reduce dataset size or upgrade plan

### Build failing?
- Check GitHub connection is active
- Verify branch name is correct (`master`)
- Check Dockerfile syntax

---

## Comparison: Northflank vs Oracle Cloud

| Feature | Northflank Free | Oracle Cloud Free |
|---------|----------------|-------------------|
| Setup time | 5 minutes | 15 minutes |
| CPU | 0.2 shared | 2 dedicated |
| RAM | 512 MB/service | 12 GB total |
| Services | 2 max | Unlimited |
| Auto-deploy | ✅ Yes | Manual |
| Public URLs | ✅ Auto HTTPS | Need ngrok |
| Complexity | Easy | Medium |

**Choose Northflank if**: You want quick setup, auto-deploy from GitHub  
**Choose Oracle Cloud if**: You need more power, want to run ngrok tunnels

---

## Next Steps

1. ✅ Deploy both services on Northflank
2. ✅ Get public URLs
3. ✅ Test API and Dashboard
4. Share URLs with your team!

Your Content Gap Analysis is now live 24/7 with automatic deployments! 🚀
