from fastapi import HTTPException
from backend.services.results_service import ResultsService

class ResultsController:
    """
    ResultsController handles HTTP requests for retrieving aggregated pipeline results,
    invokes ResultsService, and handles exceptions cleanly.
    """

    def __init__(self):
        self.results_service = ResultsService()

    def get_results(self, job_id: str) -> dict:
        """
        Processes result retrieval requests for a given job ID.

        Args:
            job_id (str): Unique job identifier (or path parameter).

        Returns:
            dict: API response payload with aggregated module results.

        Raises:
            HTTPException: 404 if job does not exist, 500 on unexpected errors.
        """
        try:
            result = self.results_service.get_all_results(job_id)
            return {
                "success": True,
                "job_id": result["resolved_job_id"],
                "results": result["results"]
            }
        except FileNotFoundError as e:
            # Respond with 404 Not Found if job record is missing
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            # Respond with 500 Internal Error for unexpected failures
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred while fetching job results: {str(e)}"
            )
