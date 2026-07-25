from pathlib import Path
from agents.highlight_agent import HighlightAgent
from backend.config import UPLOAD_DIR
from backend.services.job_service import JobService
from backend.services.result_storage_service import ResultStorageService

class HighlightService:
    """
    HighlightService coordinates highlight detection operations,
    connecting the controllers to the core HighlightAgent.
    """

    def __init__(self):
        self.highlight_agent = HighlightAgent()
        self.job_service = JobService()
        self.storage_service = ResultStorageService()

    def detect_video_highlights(
        self, 
        filename: str, 
        motion_threshold: float, 
        cooldown_seconds: float
    ) -> list:
        """
        Validates the video file existence and triggers highlight detection.

        Args:
            filename (str): The filename of the uploaded gaming video.
            motion_threshold (float): Threshold percentage of pixel differences.
            cooldown_seconds (float): Delay in seconds before another highlight can be flagged.

        Returns:
            list: List of detected highlights with timestamps.
        """
        # Sanitize filename to prevent directory traversal
        safe_filename = Path(filename).name
        video_path = UPLOAD_DIR / safe_filename

        # Ensure the file exists before invoking the agent
        if not video_path.exists():
            raise FileNotFoundError(f"Video file '{safe_filename}' not found in uploads folder.")

        # Run the detection algorithm
        return self.highlight_agent.detect_highlights(
            video_path=str(video_path),
            motion_threshold=motion_threshold,
            cooldown_seconds=cooldown_seconds
        )

    def get_highlight_data(
        self, 
        job_id: str, 
        motion_threshold: float = 8.0, 
        cooldown_seconds: float = 3.0
    ) -> list:
        """
        Retrieves highlight data. Reuses cached results if they exist,
        otherwise calculates and caches them using ResultStorageService.

        Args:
            job_id (str): The unique identifier of the job.
            motion_threshold (float): Sensitivity trigger percentage.
            cooldown_seconds (float): Delay in seconds before consecutive triggers.

        Returns:
            list: List of detected highlights.
        """
        resolved_job_id = self.job_service.resolve_job_id(job_id)

        # Return cached highlights if they exist for default parameters
        if motion_threshold == 8.0 and cooldown_seconds == 3.0:
            if self.storage_service.result_exists(resolved_job_id, "highlights.json"):
                try:
                    return self.storage_service.load_result(resolved_job_id, "highlights.json")
                except Exception:
                    pass  # Recalculate if file is corrupt

        filename = self.job_service.get_saved_filename(resolved_job_id)
        highlights = self.detect_video_highlights(filename, motion_threshold, cooldown_seconds)

        # Cache the calculated highlights using ResultStorageService
        self.storage_service.save_result(resolved_job_id, "highlights.json", highlights)

        return highlights
