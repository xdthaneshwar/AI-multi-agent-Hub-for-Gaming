from backend.services.job_service import JobService
from backend.services.result_storage_service import ResultStorageService

class ResultsService:
    """
    ResultsService aggregates all generated pipeline results for a specific job ID.
    It reuses ResultStorageService to load existing JSON artifacts without triggering re-computations.
    """

    # Mapping of response keys to result filenames
    ARTIFACT_FILES = {
        "upload": "upload.json",
        "analysis": "analysis.json",
        "highlights": "highlights.json",
        "seo": "seo.json",
        "thumbnails": "thumbnails.json",
        "creator_brief": "creator_brief.json"
    }

    def __init__(self):
        self.job_service = JobService()
        self.storage_service = ResultStorageService()

    def get_all_results(self, job_id: str) -> dict:
        """
        Loads available result artifacts for a given job ID.

        Args:
            job_id (str): Job identifier.

        Returns:
            dict: Dictionary with resolved job ID and aggregated module results.

        Raises:
            FileNotFoundError: If the job record does not exist.
        """
        # Resolve job_id (handles default placeholders and latest job ID fallback)
        resolved_job_id = self.job_service.resolve_job_id(job_id)

        # Ensure the job upload record exists before building results
        if not self.storage_service.result_exists(resolved_job_id, "upload.json"):
            raise FileNotFoundError(f"Job ID '{resolved_job_id}' does not exist.")

        results_dict = {}

        for key, filename in self.ARTIFACT_FILES.items():
            if self.storage_service.result_exists(resolved_job_id, filename):
                try:
                    results_dict[key] = self.storage_service.load_result(resolved_job_id, filename)
                except Exception:
                    results_dict[key] = None
            else:
                results_dict[key] = None

        return {
            "resolved_job_id": resolved_job_id,
            "results": results_dict
        }
