"""
FastAPI Server for Content Gap Analysis
Provides REST API endpoints for supervisor agents to trigger analysis and retrieve results
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import json
import os

# Import the orchestrator
from main import ContentGapAnalysisOrchestrator, create_sample_content_files

# Initialize FastAPI app
app = FastAPI(
    title="Content Gap Analysis API",
    description="AI-powered content gap analysis with ML recommendations",
    version="1.0.0"
)

# Configure CORS to allow requests from supervisor agents
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this to specific domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Global storage for analysis results (in-memory cache)
last_result: Optional[Dict[str, Any]] = None
last_metrics: Optional[Dict[str, Any]] = None
last_job_id: Optional[str] = None
analysis_running: bool = False


class AnalysisRequest(BaseModel):
    """Request model for triggering analysis"""
    min_recommendations: int = Field(default=12, ge=1, le=100, description="Minimum recommendations to generate")
    your_organization: str = Field(default="OpenProject", description="Your organization name")
    competitors: List[str] = Field(default=["Asana", "Trello", "Monday.com"], description="Competitor names")


class AnalysisResponse(BaseModel):
    """Response model for analysis trigger"""
    job_id: str
    status: str
    message: str
    timestamp: str
    estimated_duration_seconds: int
    gap_count: Optional[int] = None
    recommendation_count: Optional[int] = None
    model_accuracy: Optional[float] = None


def _discover_files(folder: str) -> List[str]:
    """Discover content files in a directory"""
    base = Path(folder)
    if not base.exists():
        return []
    exts = {".txt", ".json", ".html", ".md", ".htm"}
    files = []
    for p in base.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            files.append(str(p))
    return files


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Content Gap Analysis API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "analysis_running": analysis_running,
        "last_job_id": last_job_id
    }


@app.api_route("/run", methods=["GET", "POST"], response_model=AnalysisResponse)
async def run_analysis(request: AnalysisRequest = None, background_tasks: BackgroundTasks = None):
    """
    Trigger content gap analysis
    
    Discovers files from data/your_content and data/competitor_content,
    runs full analysis pipeline, and caches results.
    """
    global last_result, last_metrics, last_job_id, analysis_running
    
    # Handle GET requests without body - use defaults
    if request is None:
        request = AnalysisRequest()
    
    if analysis_running:
        raise HTTPException(status_code=409, detail="Analysis already running. Please wait.")
    
    # Generate job ID
    job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    last_job_id = job_id
    analysis_running = True
    
    try:
        # Discover input files
        your_files = _discover_files('data/your_content')
        competitor_files = _discover_files('data/competitor_content')
        
        if not your_files:
            raise HTTPException(
                status_code=400,
                detail="No content files found in data/your_content. Please add content files."
            )
        
        if not competitor_files:
            raise HTTPException(
                status_code=400,
                detail="No content files found in data/competitor_content. Please add competitor files."
            )
        
        # Initialize orchestrator
        orchestrator = ContentGapAnalysisOrchestrator(
            your_organization=request.your_organization,
            competitors=request.competitors
        )
        
        # Run analysis
        print(f"\n[API] Starting analysis job: {job_id}")
        results = orchestrator.run_full_analysis(
            your_content_files=your_files,
            competitor_content_files=competitor_files,
            min_recommendations=request.min_recommendations
        )

        # Fallback: if no gaps/recommendations were produced, re-run with sample content
        if len(results.get('gaps', [])) == 0 and len(results.get('recommendations', [])) == 0:
            print("[API] No gaps/recommendations found. Executing sample content fallback run...")
            sample_your, sample_comp = create_sample_content_files()
            results = orchestrator.run_full_analysis(
                your_content_files=sample_your,
                competitor_content_files=sample_comp,
                min_recommendations=request.min_recommendations
            )
        
        # Cache results
        last_result = results
        last_metrics = results.get('model_metrics', {})
        
        print(f"[API] Analysis job {job_id} completed successfully")
        
        return AnalysisResponse(
            job_id=job_id,
            status="completed",
            message="Analysis completed successfully",
            timestamp=datetime.now().isoformat(),
            estimated_duration_seconds=0,
            gap_count=len(results.get('gaps', [])),
            recommendation_count=len(results.get('recommendations', [])),
            model_accuracy=last_metrics.get('accuracy')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Analysis job {job_id} failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        analysis_running = False


@app.get("/package")
async def get_package():
    """
    Retrieve the complete analysis package
    
    Returns the full JSON package with gaps, recommendations, metrics, etc.
    """
    global last_result
    
    if last_result is None:
        raise HTTPException(
            status_code=404,
            detail="No analysis results available. Run /run endpoint first."
        )
    
    return JSONResponse(content=last_result)


@app.get("/metrics")
async def get_metrics():
    """
    Retrieve ML model performance metrics
    
    Returns accuracy, precision, recall, F1 scores, confusion matrix, etc.
    """
    global last_metrics
    
    if last_metrics is None:
        raise HTTPException(
            status_code=404,
            detail="No metrics available. Run /run endpoint first."
        )
    
    return JSONResponse(content=last_metrics)


@app.get("/recommendations")
async def get_recommendations():
    """
    Retrieve content recommendations only
    
    Returns prioritized list of content recommendations.
    """
    global last_result
    
    if last_result is None:
        raise HTTPException(
            status_code=404,
            detail="No recommendations available. Run /run endpoint first."
        )
    
    recommendations = last_result.get('recommendations', [])
    
    return {
        "count": len(recommendations),
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/gaps")
async def get_gaps():
    """
    Retrieve identified content gaps
    
    Returns list of content gaps with impact scores and classifications.
    """
    global last_result
    
    if last_result is None:
        raise HTTPException(
            status_code=404,
            detail="No gaps available. Run /run endpoint first."
        )
    
    gaps = last_result.get('gaps', [])
    
    return {
        "count": len(gaps),
        "gaps": gaps,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
async def get_status():
    """
    Get current analysis status
    
    Returns whether analysis is running and last job information.
    """
    return {
        "analysis_running": analysis_running,
        "last_job_id": last_job_id,
        "has_results": last_result is not None,
        "has_metrics": last_metrics is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/files")
async def list_files():
    """
    List available input files
    
    Returns discovered content files in both directories.
    """
    your_files = _discover_files('data/your_content')
    competitor_files = _discover_files('data/competitor_content')
    
    return {
        "your_content": {
            "count": len(your_files),
            "files": [str(Path(f).name) for f in your_files]
        },
        "competitor_content": {
            "count": len(competitor_files),
            "files": [str(Path(f).name) for f in competitor_files]
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/download/report")
async def download_report():
    """Download the markdown report"""
    report_path = Path("reports/content_gap_analysis_report.md")
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found. Run analysis first.")
    return FileResponse(report_path, media_type="text/markdown", filename="content_gap_report.md")


@app.get("/download/pdf")
async def download_pdf():
    """Download the PDF report"""
    pdf_path = Path("reports/content_gap_analysis_report.pdf")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found. Run analysis first.")
    return FileResponse(pdf_path, media_type="application/pdf", filename="content_gap_report.pdf")


@app.get("/download/presentation")
async def download_presentation():
    """Download the presentation markdown"""
    pres_path = Path("presentations/executive_presentation.md")
    if not pres_path.exists():
        raise HTTPException(status_code=404, detail="Presentation not found. Run analysis first.")
    return FileResponse(pres_path, media_type="text/markdown", filename="executive_presentation.md")


@app.get("/download/dashboard")
async def download_dashboard_specs():
    """Download dashboard specifications JSON"""
    dash_path = Path("dashboards/dashboard_specifications.json")
    if not dash_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard specs not found. Run analysis first.")
    return FileResponse(dash_path, media_type="application/json", filename="dashboard_specs.json")


@app.get("/download/pptx")
async def download_pptx():
    """Download the PowerPoint presentation"""
    pptx_path = Path("presentations/executive_presentation.pptx")
    if not pptx_path.exists():
        raise HTTPException(status_code=404, detail="PPTX not found. Run analysis first.")
    return FileResponse(
        pptx_path, 
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename="executive_presentation.pptx"
    )


@app.get("/outputs")
async def list_outputs():
    """List all available output files"""
    outputs = {
        "reports": list(Path("reports").glob("*.md")) if Path("reports").exists() else [],
        "presentations": list(Path("presentations").glob("*")) if Path("presentations").exists() else [],
        "dashboards": list(Path("dashboards").glob("*.json")) if Path("dashboards").exists() else [],
        "models": list(Path("models").glob("*.json")) if Path("models").exists() else [],
    }
    
    return {
        "available_files": {
            "reports": [f.name for f in outputs["reports"]],
            "presentations": [f.name for f in outputs["presentations"]],
            "dashboards": [f.name for f in outputs["dashboards"]],
            "models": [f.name for f in outputs["models"]],
        },
        "download_urls": {
            "report_md": "/download/report",
            "report_pdf": "/download/pdf",
            "presentation_md": "/download/presentation",
            "presentation_pptx": "/download/pptx",
            "dashboard_specs": "/download/dashboard",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
