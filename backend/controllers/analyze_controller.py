from fastapi import HTTPException
from backend.services.video_service import VideoService
from backend.services.job_service import JobService

class AnalyzeController:
    """
    AnalyzeController processes incoming analysis requests by coordinating
    the VideoService execution and returning results.
    """

    def __init__(self):
        self.video_service = VideoService()
        self.job_service = JobService()

    def run_analysis(self, job_id: str) -> dict:
        """
        Coordinates the analysis of a specific video file using a job ID.

        Args:
            job_id (str): Unique identifier of the upload job (or placeholder).

        Returns:
            dict: JSON-serializable response dict with status and analysis metadata.
        """
        try:
            # 1. Resolve job_id (handles default placeholders and latest job retrieval)
            resolved_job_id = self.job_service.resolve_job_id(job_id)

            # 2. Retrieve video analysis metadata via VideoService
            analysis_data = self.video_service.get_analysis_metadata(resolved_job_id)

            return {
                "success": True,
                "job_id": resolved_job_id,
                "analysis": analysis_data
            }
        except FileNotFoundError as e:
            # Respond with 404 if upload.json or the video is missing
            raise HTTPException(status_code=404, detail=str(e))
        except RuntimeError as e:
            # Respond with 400 Bad Request if media processing fails
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # Handle fallback unexpected internal exceptions
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred during video analysis: {str(e)}"
            )
