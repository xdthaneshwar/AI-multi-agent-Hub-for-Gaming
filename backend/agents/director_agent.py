from backend.services.job_service import JobService
from backend.services.video_service import VideoService
from backend.services.highlight_service import HighlightService

class DirectorAgent:
    """
    The Director Agent orchestrates the video processing pipeline.
    It triggers and retrieves results from the VideoService and HighlightService,
    combining them into a unified report.
    """

    def __init__(self):
        self.job_service = JobService()
        self.video_service = VideoService()
        self.highlight_service = HighlightService()

    def run_pipeline(self, job_id: str) -> dict:
        """
        Orchestrates and triggers the video analysis and highlight detection.
        Reuses cached results from the results directory if they exist.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            dict: Combined analysis and highlights data.
        """
        # 1. Resolve job_id (handles fallback default placeholders and latest job ID)
        resolved_job_id = self.job_service.resolve_job_id(job_id)

        # 2. Retrieve analysis metadata via VideoService (uses cache internally)
        analysis_data = self.video_service.get_analysis_metadata(resolved_job_id)

        # 3. Retrieve highlights metadata via HighlightService (uses cache internally)
        highlights_data = self.highlight_service.get_highlight_data(resolved_job_id)

        return {
            "resolved_job_id": resolved_job_id,
            "analysis": analysis_data,
            "highlights": highlights_data
        }
