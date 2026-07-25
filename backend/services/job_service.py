from pathlib import Path
from backend.config import RESULTS_DIR
from backend.services.result_storage_service import ResultStorageService

class JobService:
    """
    JobService handles retrieving, creating, and processing metadata stored 
    in the results directory. It serves as the single source of truth for job lifecycle records.
    """

    def __init__(self):
        self.storage_service = ResultStorageService()

    def create_job_metadata(self, job_id: str, original_filename: str, saved_filename: str) -> None:
        """
        Creates a job directory and saves upload metadata to results/<job_id>/upload.json.

        Args:
            job_id (str): The unique identifier of the job.
            original_filename (str): The user's original uploaded filename.
            saved_filename (str): The unique filename stored on the disk.
        """
        upload_metadata = {
            "job_id": job_id,
            "original_filename": original_filename,
            "saved_filename": saved_filename
        }
        self.storage_service.save_result(job_id, "upload.json", upload_metadata)

    def get_latest_job_id(self) -> str:
        """
        Scans the results directory and returns the job ID of the most recently uploaded video.

        Returns:
            str: The job ID of the latest upload.

        Raises:
            FileNotFoundError: If no uploaded jobs are found.
        """
        if not RESULTS_DIR.exists():
            raise FileNotFoundError("No jobs have been uploaded yet.")

        # Gather all subdirectories containing an upload.json file
        job_dirs = [
            d for d in RESULTS_DIR.iterdir()
            if d.is_dir() and (d / "upload.json").exists()
        ]

        if not job_dirs:
            raise FileNotFoundError("No jobs have been uploaded yet.")

        # Sort directories by the modification time of upload.json (newest first)
        job_dirs.sort(key=lambda d: (d / "upload.json").stat().st_mtime, reverse=True)
        return job_dirs[0].name

    def resolve_job_id(self, job_id: str) -> str:
        """
        Resolves a job_id input, checking for empty strings, FastAPI default "string",
        or Swagger example values, falling back to the latest uploaded job_id.

        Args:
            job_id (str): The input job_id.

        Returns:
            str: The resolved, active job_id.
        """
        placeholders = {"409ef1e2-b13c-41fb-9cf9-980b6754bc11", "string", "", None}
        if job_id in placeholders:
            try:
                return self.get_latest_job_id()
            except FileNotFoundError:
                raise FileNotFoundError("No uploaded videos found in the system.")
        return job_id

    def get_job_metadata(self, job_id: str) -> dict:
        """
        Retrieves the complete upload metadata dictionary from results/<job_id>/upload.json.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            dict: The metadata dictionary.

        Raises:
            FileNotFoundError: If the metadata file does not exist.
        """
        resolved_job_id = self.resolve_job_id(job_id)
        if not self.storage_service.result_exists(resolved_job_id, "upload.json"):
            raise FileNotFoundError(f"Job ID '{resolved_job_id}' does not exist or upload metadata is missing.")

        return self.storage_service.load_result(resolved_job_id, "upload.json")

    def get_saved_filename(self, job_id: str) -> str:
        """
        Reads the results/<job_id>/upload.json metadata file and extracts the saved filename.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            str: The saved video filename associated with the job.
        """
        metadata = self.get_job_metadata(job_id)
        saved_filename = metadata.get("saved_filename")
        if not saved_filename:
            raise KeyError("Field 'saved_filename' is missing in metadata.")
        return saved_filename

    def get_original_filename(self, job_id: str) -> str:
        """
        Reads the results/<job_id>/upload.json metadata file and extracts the original uploaded filename.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            str: The original filename.
        """
        metadata = self.get_job_metadata(job_id)
        original_filename = metadata.get("original_filename")
        if not original_filename:
            raise KeyError("Field 'original_filename' is missing in metadata.")
        return original_filename
