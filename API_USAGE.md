# Content Gap Analysis - API & Dashboard Usage Guide

## Overview

This system provides both a **REST API** and an **Interactive Visual Dashboard** for AI-powered content gap analysis.

- **API Server**: Port `8000` - FastAPI REST endpoints for supervisor agents
- **Dashboard**: Port `8050` - Plotly Dash visual interface with real-time charts

---

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Build and start both services
docker-compose up --build

# Or run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker (Individual Services)

```bash
# Build image
docker build -t content-gap-analysis .

# Run API server
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  content-gap-analysis

# Run Dashboard
docker run -p 8050:8050 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/content_gap_analysis_package.json:/app/content_gap_analysis_package.json \
  content-gap-analysis python dashboard_app.py
```

### Using Python Directly

```bash
# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Start API server
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, start dashboard
python dashboard_app.py
```

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. Health Check
**GET** `/health`

Check if the API is running.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Content Gap Analysis API",
  "version": "1.0.0",
  "timestamp": "2025-11-21T10:30:00",
  "analysis_running": false,
  "last_job_id": null
}
```

---

### 2. Run Analysis
**POST** `/run`

Trigger full content gap analysis pipeline.

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "min_recommendations": 15,
    "your_organization": "OpenProject",
    "competitors": ["Asana", "Trello", "Monday.com"]
  }'
```

**Request Body:**
```json
{
  "min_recommendations": 12,
  "your_organization": "OpenProject",
  "competitors": ["Asana", "Trello", "Monday.com"]
}
```

**Response:**
```json
{
  "job_id": "20251121_103000",
  "status": "completed",
  "message": "Analysis completed successfully",
  "timestamp": "2025-11-21T10:35:00",
  "estimated_duration_seconds": 0,
  "gap_count": 17,
  "recommendation_count": 17,
  "model_accuracy": 1.0
}
```

---

### 3. Get Complete Package
**GET** `/package`

Retrieve the full analysis results package (JSON).

```bash
curl http://localhost:8000/package > analysis_results.json
```

**Response:** Full JSON package with:
- `corpus_stats`: Document statistics
- `gaps`: Identified content gaps
- `recommendations`: Prioritized recommendations
- `model_metrics`: ML model performance
- `dashboard_spec`: Dashboard specifications
- `slides`: Presentation slides
- `metadata`: Analysis metadata

---

### 4. Get Model Metrics
**GET** `/metrics`

Retrieve ML model performance metrics only.

```bash
curl http://localhost:8000/metrics
```

**Response:**
```json
{
  "accuracy": 1.0,
  "precision": 1.0,
  "recall": 1.0,
  "f1_macro": 1.0,
  "f1_micro": 1.0,
  "samples_evaluated": 80,
  "confusion_matrix": [...],
  "false_positives": [],
  "false_negatives": []
}
```

---

### 5. Get Recommendations
**GET** `/recommendations`

Retrieve content recommendations only.

```bash
curl http://localhost:8000/recommendations
```

**Response:**
```json
{
  "count": 17,
  "recommendations": [
    {
      "title": "API documentation",
      "impact_score": 41,
      "difficulty": "low",
      "publish_priority": "2025-12-28",
      "intent": "informational",
      "target_keywords": [...],
      "outline": {...},
      ...
    }
  ],
  "timestamp": "2025-11-21T10:35:00"
}
```

---

### 6. Get Content Gaps
**GET** `/gaps`

Retrieve identified content gaps only.

```bash
curl http://localhost:8000/gaps
```

**Response:**
```json
{
  "count": 17,
  "gaps": [
    {
      "title": "Gantt charts",
      "gap_type": "missing-content",
      "impact_score": 85,
      "difficulty": "medium",
      "keywords": [...],
      "reason": "Competitor coverage significantly exceeds yours"
    }
  ],
  "timestamp": "2025-11-21T10:35:00"
}
```

---

### 7. Check Status
**GET** `/status`

Get current analysis status.

```bash
curl http://localhost:8000/status
```

**Response:**
```json
{
  "analysis_running": false,
  "last_job_id": "20251121_103000",
  "has_results": true,
  "has_metrics": true,
  "timestamp": "2025-11-21T10:35:00"
}
```

---

### 8. List Input Files
**GET** `/files`

List discovered content files.

```bash
curl http://localhost:8000/files
```

**Response:**
```json
{
  "your_content": {
    "count": 42,
    "files": ["openproject_docs.json", "openproject_blog.json", ...]
  },
  "competitor_content": {
    "count": 65,
    "files": ["asana_guide.json", "trello_tour.json", ...]
  },
  "timestamp": "2025-11-21T10:35:00"
}
```

---

## 📊 Visual Dashboard

Access the interactive dashboard at:

```
http://localhost:8050
```

### Features

1. **Summary Cards**
   - Total content gaps
   - Number of recommendations
   - Model accuracy
   - Roadmap timeline

2. **Gap Distribution Chart**
   - Pie chart showing gap types (missing, thin, outdated, under-optimized)

3. **Impact Score Distribution**
   - Histogram of gap impact scores (0-100)

4. **Publication Timeline**
   - Bar chart showing monthly content publication schedule

5. **Difficulty vs Impact**
   - Scatter plot showing difficulty levels vs business impact

6. **Model Performance Card**
   - Accuracy, Precision, Recall, F1 scores
   - Validation status

7. **Top 10 Recommendations Table**
   - Priority recommendations with impact scores, difficulty, dates

### Dashboard Controls

- **Refresh Button**: Manually reload data
- **Auto-refresh**: Dashboard updates every 30 seconds automatically

---

## 🔧 Supervisor Agent Integration

### Python Example

```python
import requests

API_BASE = "http://localhost:8000"

# Trigger analysis
response = requests.post(f"{API_BASE}/run", json={
    "min_recommendations": 15,
    "your_organization": "MyCompany",
    "competitors": ["Competitor1", "Competitor2"]
})

job = response.json()
print(f"Job ID: {job['job_id']}")
print(f"Gaps found: {job['gap_count']}")
print(f"Recommendations: {job['recommendation_count']}")

# Get recommendations
recs = requests.get(f"{API_BASE}/recommendations").json()
for rec in recs['recommendations'][:5]:
    print(f"- {rec['title']} (Impact: {rec['impact_score']})")

# Download full package
package = requests.get(f"{API_BASE}/package").json()
with open('analysis_package.json', 'w') as f:
    json.dump(package, f, indent=2)
```

### cURL Example

```bash
#!/bin/bash

# Run analysis
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"min_recommendations": 12}' \
  | jq .

# Wait a moment for processing
sleep 5

# Get results
curl http://localhost:8000/package > results.json

# Get just recommendations
curl http://localhost:8000/recommendations | jq '.recommendations[] | {title, impact_score, difficulty}'
```

---

## 📂 Directory Structure

```
content_gap_analysis/
├── api_server.py              # FastAPI REST API
├── dashboard_app.py           # Plotly Dash dashboard
├── main.py                    # Pipeline orchestrator
├── Dockerfile                 # Container image
├── docker-compose.yml         # Multi-service orchestration
├── requirements.txt           # Python dependencies
├── data/
│   ├── your_content/          # Your organization's content (JSON/TXT/HTML)
│   └── competitor_content/    # Competitor content
├── reports/                   # Generated PDF/Markdown reports
├── presentations/             # Generated PPTX presentations
├── models/                    # Trained ML models
└── dashboards/                # Dashboard specifications
```

---

## 🔐 Security Notes

**For Production Use:**

1. **Add Authentication**
   ```python
   # In api_server.py, add header-based auth
   from fastapi import Header, HTTPException
   
   async def verify_token(x_api_key: str = Header(...)):
       if x_api_key != os.getenv("API_KEY"):
           raise HTTPException(401, "Invalid API key")
   ```

2. **Use Environment Variables**
   ```yaml
   # In docker-compose.yml
   environment:
     - API_KEY=${API_KEY}
     - ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. **Enable CORS** (if needed for web clients)
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_methods=["*"],
       allow_headers=["*"]
   )
   ```

---

## 🐛 Troubleshooting

### API returns 404 for /package
- Run `/run` endpoint first to generate analysis results

### Dashboard shows "No data available"
- Ensure `content_gap_analysis_package.json` exists
- Run analysis via API or `python main.py`

### Container fails to start
- Check logs: `docker-compose logs`
- Verify data files exist in `data/your_content` and `data/competitor_content`

### Port already in use
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # API
  - "8051:8050"  # Dashboard
```

---

## 📈 Performance Tips

1. **Limit Input Files**: Analysis time scales with content volume
2. **Use Docker Volumes**: Mount data directories for faster access
3. **Pre-download Models**: Include in Dockerfile to avoid runtime downloads
4. **Cache Results**: API stores last result in memory for fast retrieval

---

## 🎯 Next Steps

1. **Run Analysis**
   ```bash
   curl -X POST http://localhost:8000/run
   ```

2. **View Dashboard**
   - Open browser to `http://localhost:8050`

3. **Integrate with Supervisor Agent**
   - Use `/run` to trigger analysis
   - Poll `/status` for completion
   - Retrieve `/package` for full results

4. **Export Results**
   - PDF report: `reports/content_gap_analysis_report.pdf`
   - PPTX slides: `presentations/executive_presentation.pptx`
   - JSON package: `content_gap_analysis_package.json`

---

## 📚 API Documentation

Interactive API docs available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---


For issues or questions:
- Check logs: `docker-compose logs -f`
- Review README.md for setup instructions
- Verify input data in `data/` directories
