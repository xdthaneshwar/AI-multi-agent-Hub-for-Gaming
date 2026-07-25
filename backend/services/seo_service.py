from backend.services.job_service import JobService
from backend.services.video_service import VideoService
from backend.services.result_storage_service import ResultStorageService
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
        self.storage_service = ResultStorageService()

    def generate_video_seo(self, job_id: str) -> dict:
        """
        Generates (or retrieves from cache) the SEO content for a video using ResultStorageService.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            dict: The generated or cached SEO metadata (title, description, tags, hashtags).

        Raises:
            FileNotFoundError: If the job upload metadata is missing.
        """
        # 1. Resolve job_id (handles fallback default placeholders and latest job ID)
        resolved_job_id = self.job_service.resolve_job_id(job_id)

        # 2. Check if pre-calculated SEO already exists in cache via ResultStorageService
        if self.storage_service.result_exists(resolved_job_id, "seo.json"):
            try:
                return self.storage_service.load_result(resolved_job_id, "seo.json")
            except Exception:
                pass  # Fallback to recalculation if JSON file is corrupt

        # 3. Retrieve original filename
        original_filename = self.job_service.get_original_filename(resolved_job_id)

        # 4. Retrieve or calculate video metadata using VideoService (handles caching internally)
        analysis_data = self.video_service.get_analysis_metadata(resolved_job_id)

        # 5. Generate SEO content via SEOAgent
        seo_data = self.seo_agent.generate_seo(original_filename, analysis_data)

        # 6. Cache the generated SEO details via ResultStorageService
        self.storage_service.save_result(resolved_job_id, "seo.json", seo_data)

        return seo_data
