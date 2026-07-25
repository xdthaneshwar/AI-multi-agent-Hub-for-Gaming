from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.controllers.director_controller import DirectorController

# Setup router with tags to structure FastAPI docs
router = APIRouter(tags=["Director"])
controller = DirectorController()

class DirectorRequest(BaseModel):
    """
    Pydantic request body schema for the director endpoint.
    """
    job_id: str = Field(
        ...,
        description="The unique job identifier returned by the upload API",
        examples=["409ef1e2-b13c-41fb-9cf9-980b6754bc11"]
    )

@router.post("/director")
def run_director(request: DirectorRequest):
    """
    Triggers the multi-agent pipeline orchestration.

    Accepts the job_id, resolves it to the video internally (falling back to the latest 
    uploaded video if default placeholders are sent), runs both analysis and highlight 
    detection agents, and returns a combined payload.
    """
    return controller.run_director_pipeline(request.job_id)
