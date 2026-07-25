from fastapi import HTTPException
from backend.services.seo_service import SEOService
from backend.services.job_service import JobService

class SEOController:
    """
    SEOController processes incoming requests for generating SEO metadata,
    coordinates the SEOService, and handles exceptions gracefully.
    """

    def __init__(self):
        self.seo_service = SEOService()
        self.job_service = JobService()

    def run_seo_generation(self, job_id: str) -> dict:
        """
        Coordinates the SEO generation for a specific video job.

        Args:
            job_id (str): The unique identifier of the job (or placeholder).

        Returns:
            dict: API response payload with success status and generated SEO data.
        """
        try:
            # 1. Resolve job_id (handles fallback default placeholders and latest job ID)
            resolved_job_id = self.job_service.resolve_job_id(job_id)

            # 2. Execute SEO generation using the service layer
            seo_data = self.seo_service.generate_video_seo(resolved_job_id)

            return {
                "success": True,
                "job_id": resolved_job_id,
                "seo": seo_data
            }
        except FileNotFoundError as e:
            # Respond with 404 if upload.json or video file is missing
            raise HTTPException(status_code=404, detail=str(e))
        except RuntimeError as e:
            # Respond with 400 Bad Request if media processing fails
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # Handle fallback unexpected internal exceptions
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred during SEO generation: {str(e)}"
            )
