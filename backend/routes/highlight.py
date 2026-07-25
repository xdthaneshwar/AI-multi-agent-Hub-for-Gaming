from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.controllers.highlight_controller import HighlightController

# Setup router with tags to structure FastAPI auto-docs
router = APIRouter(tags=["Highlights"])
controller = HighlightController()

class HighlightRequest(BaseModel):
    """
    Pydantic request body schema for the highlight endpoint.
    """
    job_id: str = Field(
        ...,
        description="The unique job identifier returned by the upload API"
        
    )
    motion_threshold: float = Field(
        8.0,
        description="Threshold percentage of pixel differences to identify a highlight (1.0 to 100.0)",
        ge=0.1,
        le=100.0
    )
    cooldown_seconds: float = Field(
        3.0,
        description="Cooldown duration in seconds to ignore adjacent peaks after a highlight detection",
        ge=0.0
    )

@router.post("/highlight")
def detect_highlights(request: HighlightRequest):
    """
    Analyzes an uploaded video frame-by-frame to identify high-motion highlights.

    Accepts the stored video job ID, motion threshold, and cooldown timer, 
    and returns a list of detected highlights with visual motion intensity scores.
    """
    return controller.run_highlight_detection(
        job_id=request.job_id,
        motion_threshold=request.motion_threshold,
        cooldown_seconds=request.cooldown_seconds
    )
