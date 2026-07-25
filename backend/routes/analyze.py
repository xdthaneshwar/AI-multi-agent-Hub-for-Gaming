from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.controllers.analyze_controller import AnalyzeController

# Setup routing with tags for self-documenting API
router = APIRouter(tags=["Analysis"])
controller = AnalyzeController()

class AnalyzeRequest(BaseModel):
    """
    Pydantic request body schema for the analyze endpoint.
    """
    job_id: str = Field(
        ..., 
        description="The unique job identifier returned by the upload API"
        
    )

@router.post("/analyze")
def analyze_video(request: AnalyzeRequest):
    """
    Triggers technical video analysis (metadata extraction) for an uploaded video.

    Accepts the job_id, resolves the filename internally, extracts duration, FPS, 
    frames, resolution, format, and size, and returns the analyzed properties.
    """
    return controller.run_analysis(request.job_id)
