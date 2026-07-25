from fastapi import APIRouter
from backend.controllers.results_controller import ResultsController

# Setup router with tags to structure FastAPI docs
router = APIRouter(tags=["Results"])
controller = ResultsController()

@router.get("/results/{job_id}")
def get_job_results(job_id: str):
    """
    Retrieves all stored AI module results and metadata for a video job.

    Accepts the job_id as a path parameter, loads all existing artifacts from storage
    without re-calculating outputs, and returns null for ungenerated module fields.
    """
    return controller.get_results(job_id)
