import json
from pathlib import Path
from backend.config import THUMBNAILS_DIR, RESULTS_DIR, UPLOAD_DIR
from backend.services.job_service import JobService
from backend.services.highlight_service import HighlightService
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

    def generate_video_thumbnails(self, job_id: str) -> list:
        """
        Generates (or retrieves from cache) thumbnail candidate previews for a video job.

        The job_id passed here is assumed to be already resolved (not a placeholder).
        Resolution is performed once by the controller layer.

        Args:
            job_id (str): The resolved, unique identifier of the job.

        Returns:
            list: List of generated thumbnails metadata dictionaries.

        Raises:
            FileNotFoundError: If the job metadata or video file is missing.
        """
        # Sanitize job_id to safe directory name (prevent traversal)
        safe_job_id = Path(job_id).name
        job_results_dir = RESULTS_DIR / safe_job_id

        # Define paths for thumbnails output and metadata cache file
        thumbnails_cache_file = job_results_dir / "thumbnails.json"
        output_dir = THUMBNAILS_DIR / safe_job_id

        # 1. Return cached result if it already exists
        if thumbnails_cache_file.exists():
            try:
                with open(thumbnails_cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass  # Fallback to regeneration if the cache file is corrupt

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

        # 5. Cache the thumbnails metadata list for future instant reads
        job_results_dir.mkdir(parents=True, exist_ok=True)
        with open(thumbnails_cache_file, "w", encoding="utf-8") as f:
            json.dump(thumbnails, f, indent=4)

        return thumbnails
