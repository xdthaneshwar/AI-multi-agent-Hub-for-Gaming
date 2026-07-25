from fastapi import HTTPException
from backend.services.thumbnail_service import ThumbnailService
from backend.services.job_service import JobService


class ThumbnailController:
    """
    ThumbnailController processes incoming thumbnail generation requests,
    coordinates the ThumbnailService, and handles exceptions gracefully.
    """

    def __init__(self):
        self.thumbnail_service = ThumbnailService()
        self.job_service = JobService()

    def run_thumbnail_generation(self, job_id: str) -> dict:
        """
        Coordinates thumbnail generation for a specific video job.

        Args:
            job_id (str): The unique job identifier (or placeholder value).

        Returns:
            dict: API response payload with success status, job_id,
                  thumbnail count, and list of thumbnail metadata.
        """
        try:
            # 1. Resolve job_id (handles default placeholders and latest job fallback)
            resolved_job_id = self.job_service.resolve_job_id(job_id)

            # 2. Execute thumbnail generation using the service layer
            thumbnails = self.thumbnail_service.generate_video_thumbnails(resolved_job_id)

            return {
                "success": True,
                "job_id": resolved_job_id,
                "thumbnail_count": len(thumbnails),
                "thumbnails": thumbnails
            }
        except FileNotFoundError as e:
            # 404 Not Found: job metadata or video file is missing
            raise HTTPException(status_code=404, detail=str(e))
        except RuntimeError as e:
            # 400 Bad Request: video processing failure (e.g. OpenCV cannot open file)
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # 500 Internal Server Error: unexpected system-level failure
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred during thumbnail generation: {str(e)}"
            )
