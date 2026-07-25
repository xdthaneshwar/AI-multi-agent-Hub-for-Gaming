from backend.services.job_service import JobService
from backend.services.video_service import VideoService
from backend.services.highlight_service import HighlightService
from backend.services.seo_service import SEOService
from backend.services.thumbnail_service import ThumbnailService
from backend.services.result_storage_service import ResultStorageService
from backend.agents.creator_brief_agent import CreatorBriefAgent

class CreatorBriefService:
    """
    CreatorBriefService orchestrates the collection of metadata from all sub-services
    (VideoService, HighlightService, SEOService, ThumbnailService) and passes them to CreatorBriefAgent.
    """

    def __init__(self):
        self.job_service = JobService()
        self.video_service = VideoService()
        self.highlight_service = HighlightService()
        self.seo_service = SEOService()
        self.thumbnail_service = ThumbnailService()
        self.creator_brief_agent = CreatorBriefAgent()
        self.storage_service = ResultStorageService()

    def get_creator_brief(self, job_id: str) -> dict:
        """
        Gathers analysis, highlights, SEO, and thumbnails for a job ID,
        and generates (or loads cached) creator brief data using ResultStorageService.

        Args:
            job_id (str): Resolved unique job identifier.

        Returns:
            dict: The structured creator brief dictionary.
        """
        # 1. Return pre-calculated creator brief if available in cache via ResultStorageService
        if self.storage_service.result_exists(job_id, "creator_brief.json"):
            try:
                return self.storage_service.load_result(job_id, "creator_brief.json")
            except Exception:
                pass  # Fallback to regeneration if file is corrupt

        # 2. Reuse existing services to obtain component data without duplicating logic
        analysis_data = self.video_service.get_analysis_metadata(job_id)
        highlights_data = self.highlight_service.get_highlight_data(job_id)
        seo_data = self.seo_service.generate_video_seo(job_id)
        thumbnails_data = self.thumbnail_service.generate_video_thumbnails(job_id)

        # 3. Generate structured creator brief via agent
        creator_brief = self.creator_brief_agent.generate_brief(
            analysis=analysis_data,
            highlights=highlights_data,
            seo=seo_data,
            thumbnails=thumbnails_data
        )

        # 4. Cache creator brief results via ResultStorageService
        self.storage_service.save_result(job_id, "creator_brief.json", creator_brief)

        return creator_brief
