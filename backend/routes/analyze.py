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
    filename: str = Field(
        ..., 
        description="The filename of the uploaded gaming video (e.g. including UUID prefix)",
        examples=["409ef1e2-b13c-41fb-9cf9-980b6754bc11_gameplay.mp4"]
    )

@router.post("/analyze")
def analyze_video(request: AnalyzeRequest):
    """
    Triggers technical video analysis (metadata extraction) for an uploaded video.

    Accepts the stored video filename, extracts duration, FPS, frames, resolution, 
    format, and size, and returns the analyzed properties.
    """
    return controller.run_analysis(request.filename)
