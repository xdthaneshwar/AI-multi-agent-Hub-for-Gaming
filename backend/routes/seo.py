from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.controllers.seo_controller import SEOController

# Setup router with tags to structure FastAPI docs
router = APIRouter(tags=["SEO"])
controller = SEOController()

class SEORequest(BaseModel):
    """
    Pydantic request body schema for the SEO endpoint.
    """
    job_id: str = Field(
        ...,
        description="The unique job identifier returned by the upload API",
        examples=["409ef1e2-b13c-41fb-9cf9-980b6754bc11"]
    )

@router.post("/seo")
def generate_seo(request: SEORequest):
    """
    Triggers the generation of optimized SEO metadata for a video.

    Accepts the job_id, resolves the video file internally (supports placeholder fallback),
    and generates an optimized title, description, tags, and hashtags.
    """
    return controller.run_seo_generation(request.job_id)
