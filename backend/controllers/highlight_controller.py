from fastapi import HTTPException
from backend.services.highlight_service import HighlightService
from backend.services.job_service import JobService

class HighlightController:
    """
    HighlightController manages HTTP incoming parameters, runs highlight
    detection by coordinating HighlightService, and returns responses.
    """

    def __init__(self):
        self.highlight_service = HighlightService()
        self.job_service = JobService()

    def run_highlight_detection(
        self, 
        job_id: str, 
        motion_threshold: float, 
        cooldown_seconds: float
    ) -> dict:
        """
        Coordinates the detection of video highlights using a job ID.

        Args:
            job_id (str): Unique identifier of the upload job (or placeholder).
            motion_threshold (float): Sensitivity percentage for motion trigger.
            cooldown_seconds (float): Ignore-period post-detection to avoid redundancies.

        Returns:
            dict: API response dict containing success indicator and highlights list.
        """
        try:
            # 1. Resolve job_id (handles default placeholders and latest job retrieval)
            resolved_job_id = self.job_service.resolve_job_id(job_id)

            # 2. Retrieve highlights using the service (handles caching internally)
            highlights = self.highlight_service.get_highlight_data(
                job_id=resolved_job_id,
                motion_threshold=motion_threshold,
                cooldown_seconds=cooldown_seconds
            )
            
            return {
                "success": True,
                "job_id": resolved_job_id,
                "highlight_count": len(highlights),
                "highlights": highlights
            }
        except FileNotFoundError as e:
            # 404 Not Found if video or metadata is missing
            raise HTTPException(status_code=404, detail=str(e))
        except RuntimeError as e:
            # 400 Bad Request if media processing fails
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # 500 Internal Error for system issues
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred during highlight detection: {str(e)}"
            )
