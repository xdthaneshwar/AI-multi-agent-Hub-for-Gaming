from fastapi import APIRouter
from backend.controllers.status_controller import StatusController

# Setup router with tags to structure FastAPI docs
router = APIRouter(tags=["Status"])
controller = StatusController()

@router.get("/status/{job_id}")
def get_job_status(job_id: str):
    """
    Retrieves the pipeline completion status and progress percentage for a video job.

    Accepts the job_id as a path parameter, checks all module artifacts in storage
    without re-calculating outputs, and returns the completion metrics.
    """
    return controller.get_status(job_id)
