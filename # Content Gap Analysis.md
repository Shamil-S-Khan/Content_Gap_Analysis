# Content Gap Analysis

AI-powered content gap analysis and recommendation system.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Run Analysis
```bash
python main.py
```

### 3. Access Services

**Local:**
- API: http://localhost:8000
- Dashboard: http://localhost:8050
- API Docs: http://localhost:8000/docs

**Public (Oracle Cloud):**
- API: https://busked-schematically-amiyah.ngrok-free.dev
- Dashboard: https://hyun-unoverwhelmed-jaycob.ngrok-free.dev

## Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Endpoints

- `POST /run` - Run analysis
- `GET /recommendations` - Get recommendations
- `GET /gaps` - Get content gaps
- `GET /metrics` - Model metrics
- `GET /download/pdf` - Download PDF report
- `GET /download/pptx` - Download PowerPoint

## Output Files

- `content_gap_analysis_package.json` - Complete results
- `reports/content_gap_analysis_report.pdf` - PDF report
- `presentations/executive_presentation.pptx` - PowerPoint
- `models/model_evaluation_metrics.json` - Model performance

## Stack

- **Backend**: FastAPI, Python 3.11
- **ML**: scikit-learn, spaCy, NLTK
- **Dashboard**: Dash, Plotly
- **Deployment**: Docker, ngrok, Oracle Cloud
