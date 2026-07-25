import json
from pathlib import Path
from backend.config import RESULTS_DIR
from backend.services.job_service import JobService
from backend.services.video_service import VideoService
from backend.agents.seo_agent import SEOAgent

class SEOService:
    """
    SEOService coordinates the generation and caching of SEO metadata,
    bridging controllers with JobService, VideoService, and SEOAgent.
    """

    def __init__(self):
        self.job_service = JobService()
        self.video_service = VideoService()
        self.seo_agent = SEOAgent()

    def generate_video_seo(self, job_id: str) -> dict:
        """
        Generates (or retrieves from cache) the SEO content for a video.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            dict: The generated or cached SEO metadata (title, description, tags, hashtags).

        Raises:
            FileNotFoundError: If the job upload metadata is missing.
        """
        # 1. Resolve job_id (handles fallback default placeholders and latest job ID)
        resolved_job_id = self.job_service.resolve_job_id(job_id)
        
        safe_job_id = Path(resolved_job_id).name
        job_results_dir = RESULTS_DIR / safe_job_id
        seo_file = job_results_dir / "seo.json"

        # 2. Check if pre-calculated SEO already exists in cache
        if seo_file.exists():
            try:
                with open(seo_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass  # Fallback to recalculation if JSON file is corrupt

        # 3. Retrieve original filename
        original_filename = self.job_service.get_original_filename(resolved_job_id)

        # 4. Retrieve or calculate video metadata using VideoService (handles caching internally)
        analysis_data = self.video_service.get_analysis_metadata(resolved_job_id)

        # 5. Generate SEO content via SEOAgent
        seo_data = self.seo_agent.generate_seo(original_filename, analysis_data)

        # 6. Cache the generated SEO details
        job_results_dir.mkdir(parents=True, exist_ok=True)
        with open(seo_file, "w", encoding="utf-8") as f:
            json.dump(seo_data, f, indent=4)

        return seo_data
