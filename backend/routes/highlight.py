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
    filename: str = Field(
        ...,
        description="The filename of the uploaded gaming video (including UUID prefix)",
        examples=["409ef1e2-b13c-41fb-9cf9-980b6754bc11_gameplay.mp4"]
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

    Accepts the stored video filename, motion threshold, and cooldown timer, 
    and returns a list of detected highlights with visual motion intensity scores.
    """
    return controller.run_highlight_detection(
        filename=request.filename,
        motion_threshold=request.motion_threshold,
        cooldown_seconds=request.cooldown_seconds
    )
