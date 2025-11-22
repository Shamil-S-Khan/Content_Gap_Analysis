# Content Gap Analysis - Docker & API Quick Reference

## 🚀 Quick Start Commands

### Docker Compose (Easiest)
```bash
# Start everything (API + Dashboard)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

### Local Development
```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Or manually:
uvicorn api_server:app --reload &
python dashboard_app.py
```

## 📍 Access Points

- **API**: http://localhost:8000
  - Swagger Docs: http://localhost:8000/docs
  - Health Check: http://localhost:8000/health
  
- **Dashboard**: http://localhost:8050

## 🔌 Supervisor Agent Integration

### Minimal Example (Python)
```python
import requests

# Trigger analysis
response = requests.post("http://localhost:8000/run")
job = response.json()
print(f"Analysis complete: {job['recommendation_count']} recommendations")

# Get results
results = requests.get("http://localhost:8000/package").json()
```

### Minimal Example (cURL)
```bash
# Run analysis
curl -X POST http://localhost:8000/run | jq .

# Get recommendations
curl http://localhost:8000/recommendations | jq '.recommendations[0]'
```

## 📊 Dashboard Features

1. **Summary Cards** - Gaps, recommendations, accuracy, timeline
2. **Gap Distribution** - Pie chart by gap type
3. **Impact Scores** - Histogram of business impact
4. **Publication Timeline** - Monthly content schedule
5. **Difficulty Matrix** - Scatter plot: difficulty vs impact
6. **Model Metrics** - ML performance dashboard
7. **Top Recommendations** - Priority table with dates

Auto-refreshes every 30 seconds.

## 🐳 Docker Commands

```bash
# Build only
docker-compose build

# Rebuild from scratch
docker-compose build --no-cache

# Start specific service
docker-compose up api
docker-compose up dashboard

# Scale (if needed)
docker-compose up --scale dashboard=2

# Clean up volumes
docker-compose down -v
```

## 🔧 Troubleshooting

**Port conflict?**
```bash
# Edit docker-compose.yml ports section
ports:
  - "8001:8000"  # Change left number
```

**No data showing?**
```bash
# Ensure data files exist
ls data/your_content/
ls data/competitor_content/

# Run analysis first
curl -X POST http://localhost:8000/run
```

**Container won't start?**
```bash
# Check logs
docker-compose logs api
docker-compose logs dashboard

# Restart specific service
docker-compose restart api
```

## 📦 Output Files

After running analysis:
- `content_gap_analysis_package.json` - Full results
- `reports/content_gap_analysis_report.pdf` - PDF report
- `presentations/executive_presentation.pptx` - Slides
- `models/model_evaluation_metrics.json` - ML metrics

## 🎯 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/run` | POST | Trigger analysis |
| `/package` | GET | Full results JSON |
| `/metrics` | GET | Model performance |
| `/recommendations` | GET | Content recommendations |
| `/gaps` | GET | Content gaps |
| `/status` | GET | Current status |
| `/files` | GET | List input files |

Full documentation: [API_USAGE.md](API_USAGE.md)
