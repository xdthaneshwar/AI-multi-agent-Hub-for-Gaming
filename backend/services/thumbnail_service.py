from pathlib import Path
from backend.config import THUMBNAILS_DIR, UPLOAD_DIR
from backend.services.job_service import JobService
from backend.services.highlight_service import HighlightService
from backend.services.result_storage_service import ResultStorageService
from backend.agents.thumbnail_agent import ThumbnailAgent

class ThumbnailService:
    """
    ThumbnailService coordinates the extraction, saving, and caching of video thumbnails,
    bridging controllers with JobService, HighlightService, and ThumbnailAgent.
    """

    def __init__(self):
        self.job_service = JobService()
        self.highlight_service = HighlightService()
        self.thumbnail_agent = ThumbnailAgent()
        self.storage_service = ResultStorageService()

    def generate_video_thumbnails(self, job_id: str) -> list:
        """
        Generates (or retrieves from cache) thumbnail candidate previews for a video job.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            list: List of generated thumbnails metadata dictionaries.

        Raises:
            FileNotFoundError: If the job metadata or video file is missing.
        """
        # Sanitize job_id to safe directory name (prevent traversal)
        safe_job_id = Path(job_id).name
        output_dir = THUMBNAILS_DIR / safe_job_id

        # 1. Check if pre-calculated thumbnails metadata already exists in cache via ResultStorageService
        if self.storage_service.result_exists(job_id, "thumbnails.json"):
            try:
                return self.storage_service.load_result(job_id, "thumbnails.json")
            except Exception:
                pass  # Fallback to regeneration if cache is corrupt

        # 2. Resolve the saved video filename from job metadata
        filename = self.job_service.get_saved_filename(job_id)
        video_path = UPLOAD_DIR / filename

        # 3. Retrieve highlights (uses HighlightService cache internally — no duplicate detection)
        highlights = self.highlight_service.get_highlight_data(job_id)

        # 4. Extract and save thumbnails via ThumbnailAgent
        thumbnails = self.thumbnail_agent.extract_thumbnails(
            video_path=str(video_path),
            highlights=highlights,
            output_dir=output_dir
        )

        # 5. Cache the thumbnails metadata list via ResultStorageService
        self.storage_service.save_result(job_id, "thumbnails.json", thumbnails)

        return thumbnails
