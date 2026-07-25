from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.controllers.creator_brief_controller import CreatorBriefController

# Setup router with tags to structure FastAPI docs
router = APIRouter(tags=["Creator Brief"])
controller = CreatorBriefController()

class CreatorBriefRequest(BaseModel):
    """
    Pydantic request body schema for the Creator Brief endpoint.
    """
    job_id: str = Field(
        ...,
        description="The unique job identifier returned by the upload API",
        examples=["409ef1e2-b13c-41fb-9cf9-980b6754bc11"]
    )

@router.post("/creator-brief")
def generate_creator_brief(request: CreatorBriefRequest):
    """
    Generates a comprehensive creator brief combining video analysis, highlights,
    SEO metadata, and thumbnail previews into a single structured report.
    """
    return controller.run_creator_brief_pipeline(request.job_id)
