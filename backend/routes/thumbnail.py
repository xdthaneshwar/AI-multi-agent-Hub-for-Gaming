from fastapi import APIRouter
from pydantic import BaseModel, Field
from backend.controllers.thumbnail_controller import ThumbnailController

# Setup router with tags to organise FastAPI docs
router = APIRouter(tags=["Thumbnail"])
controller = ThumbnailController()


class ThumbnailRequest(BaseModel):
    """
    Pydantic request body schema for the Thumbnail endpoint.
    """
    job_id: str = Field(
        ...,
        description="The unique job identifier returned by the upload API",
        examples=["409ef1e2-b13c-41fb-9cf9-980b6754bc11"]
    )


@router.post("/thumbnail")
def generate_thumbnails(request: ThumbnailRequest):
    """
    Extracts thumbnail candidate frames from the detected highlight timestamps of a video.

    Accepts a job_id, resolves the video file internally (supports placeholder fallback),
    reuses existing highlight detection results, and extracts frames at action moments
    using OpenCV. Returns a list of saved thumbnail paths.
    """
    return controller.run_thumbnail_generation(request.job_id)
