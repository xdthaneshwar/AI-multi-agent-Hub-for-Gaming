from fastapi import HTTPException
from backend.services.status_service import StatusService

class StatusController:
    """
    StatusController handles HTTP requests for pipeline progress status,
    invokes StatusService, and handles exceptions cleanly.
    """

    def __init__(self):
        self.status_service = StatusService()

    def get_status(self, job_id: str) -> dict:
        """
        Processes status check requests for a given job ID.

        Args:
            job_id (str): Unique job identifier (or path parameter).

        Returns:
            dict: API response payload with progress details.

        Raises:
            HTTPException: 404 if job does not exist, 500 on unexpected errors.
        """
        try:
            result = self.status_service.get_job_status(job_id)
            return {
                "success": True,
                "job_id": result["resolved_job_id"],
                "status": result["status"],
                "completed_steps": result["completed_steps"],
                "total_steps": result["total_steps"],
                "progress_percentage": result["progress_percentage"]
            }
        except FileNotFoundError as e:
            # Respond with 404 Not Found if job upload record is missing
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            # Respond with 500 Internal Error for unexpected failures
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while checking job status: {str(e)}"
            )
