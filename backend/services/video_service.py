from pathlib import Path
from agents.analyze_agent import AnalyzeAgent
from backend.config import UPLOAD_DIR
from backend.services.job_service import JobService
from backend.services.result_storage_service import ResultStorageService

class VideoService:
    """
    VideoService coordinates backend operations related to video manipulation,
    bridging controllers with external processing agents.
    """

    def __init__(self):
        self.analyze_agent = AnalyzeAgent()
        self.job_service = JobService()
        self.storage_service = ResultStorageService()

    def analyze_video_file(self, filename: str) -> dict:
        """
        Validates the video file existence and triggers the AnalyzeAgent.

        Args:
            filename (str): The filename of the uploaded video.

        Returns:
            dict: Extracted video metadata dictionary.
        """
        # Sanitize input path to prevent directory traversal vulnerabilities
        safe_filename = Path(filename).name
        video_path = UPLOAD_DIR / safe_filename

        # Ensure the file exists in the uploads directory
        if not video_path.exists():
            raise FileNotFoundError(f"Video file '{safe_filename}' not found in uploads folder.")

        # Trigger analysis via the AnalyzeAgent
        return self.analyze_agent.analyze_video(str(video_path))

    def get_analysis_metadata(self, job_id: str) -> dict:
        """
        Retrieves video analysis metadata. Reuses cached results if they exist,
        otherwise calculates and caches them using ResultStorageService.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            dict: Extracted video metadata dictionary.
        """
        resolved_job_id = self.job_service.resolve_job_id(job_id)

        # Check if pre-calculated analysis exists to return instantly
        if self.storage_service.result_exists(resolved_job_id, "analysis.json"):
            try:
                return self.storage_service.load_result(resolved_job_id, "analysis.json")
            except Exception:
                pass  # Fallback to recalculation if JSON is corrupt

        # Resolve job_id to filename using JobService
        filename = self.job_service.get_saved_filename(resolved_job_id)

        # Execute analysis pipeline using analyze_video_file
        analysis_data = self.analyze_video_file(filename)
        
        # Cache the newly calculated analysis data using ResultStorageService
        self.storage_service.save_result(resolved_job_id, "analysis.json", analysis_data)

        return analysis_data
