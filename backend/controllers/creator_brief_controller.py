from fastapi import HTTPException
from backend.services.creator_brief_service import CreatorBriefService
from backend.services.job_service import JobService

class CreatorBriefController:
    """
    CreatorBriefController processes incoming requests for creator brief generation,
    coordinates CreatorBriefService, and handles HTTP exceptions.
    """

    def __init__(self):
        self.creator_brief_service = CreatorBriefService()
        self.job_service = JobService()

    def run_creator_brief_pipeline(self, job_id: str) -> dict:
        """
        Coordinates the creator brief pipeline execution.

        Args:
            job_id (str): Unique job identifier (or placeholder).

        Returns:
            dict: API response payload with success status, resolved job_id, and creator_brief data.
        """
        try:
            # 1. Resolve job_id (handles default placeholders and latest job fallback)
            resolved_job_id = self.job_service.resolve_job_id(job_id)

            # 2. Execute creator brief service
            creator_brief = self.creator_brief_service.get_creator_brief(resolved_job_id)

            return {
                "success": True,
                "job_id": resolved_job_id,
                "creator_brief": creator_brief
            }
        except FileNotFoundError as e:
            # Respond with 404 if upload metadata or video file is missing
            raise HTTPException(status_code=404, detail=str(e))
        except RuntimeError as e:
            # Respond with 400 Bad Request if video processing fails
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # Handle fallback unexpected internal exceptions
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while generating creator brief: {str(e)}"
            )
