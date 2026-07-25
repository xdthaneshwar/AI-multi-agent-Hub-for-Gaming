from backend.services.job_service import JobService
from backend.services.result_storage_service import ResultStorageService

class StatusService:
    """
    StatusService checks the completion status of all AI pipeline modules for a given job.
    It reuses ResultStorageService to inspect cached JSON artifacts without triggering re-computations.
    """

    # List of standard pipeline artifacts to monitor
    PIPELINE_FILES = {
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

    def get_job_status(self, job_id: str) -> dict:
        """
        Inspects results/<job_id>/ for module artifacts and calculates completion metrics.

        Args:
            job_id (str): Job identifier.

        Returns:
            dict: Status summary dictionary containing status per step, completed step count,
                  total steps, and progress percentage.

        Raises:
            FileNotFoundError: If the job record does not exist.
        """
        # Resolve job_id (handles default placeholders and latest job ID fallback)
        resolved_job_id = self.job_service.resolve_job_id(job_id)

        # Check if the job upload record exists
        if not self.storage_service.result_exists(resolved_job_id, "upload.json"):
            raise FileNotFoundError(f"Job ID '{resolved_job_id}' does not exist.")

        status_dict = {}
        completed_steps = 0
        total_steps = len(self.PIPELINE_FILES)

        for step_name, filename in self.PIPELINE_FILES.items():
            exists = self.storage_service.result_exists(resolved_job_id, filename)
            status_dict[step_name] = exists
            if exists:
                completed_steps += 1

        progress_percentage = round((completed_steps / total_steps) * 100, 2)

        return {
            "resolved_job_id": resolved_job_id,
            "status": status_dict,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "progress_percentage": progress_percentage
        }
