from fastapi import HTTPException
from backend.services.director_service import DirectorService

class DirectorController:
    """
    DirectorController processes incoming HTTP requests to orchestrate the video pipeline,
    manages the business execution, and returns structured API responses.
    """

    def __init__(self):
        self.director_service = DirectorService()

    def run_director_pipeline(self, job_id: str) -> dict:
        """
        Executes the director pipeline for the given job_id.

        Args:
            job_id (str): The job identifier.

        Returns:
            dict: Structured API response JSON.
        """
        try:
            results = self.director_service.process_video_job(job_id)
            return {
                "success": True,
                "job_id": results["resolved_job_id"],
                "analysis": results["analysis"],
                "highlights": results["highlights"]
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
                detail=f"An unexpected error occurred during pipeline orchestration: {str(e)}"
            )
