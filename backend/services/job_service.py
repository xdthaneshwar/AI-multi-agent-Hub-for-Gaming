import json
from pathlib import Path
from backend.config import RESULTS_DIR

class JobService:
    """
    JobService handles retrieving and processing metadata stored in the results directory.
    """

    def get_saved_filename(self, job_id: str) -> str:
        """
        Reads the results/<job_id>/upload.json metadata file and extracts the saved filename.

        Args:
            job_id (str): The unique identifier of the job.

        Returns:
            str: The saved video filename associated with the job.

        Raises:
            FileNotFoundError: If the job's upload metadata does not exist.
        """
        # Sanitize job_id to prevent path traversal issues
        safe_job_id = Path(job_id).name
        metadata_file = RESULTS_DIR / safe_job_id / "upload.json"

        if not metadata_file.exists():
            raise FileNotFoundError(f"Job ID '{safe_job_id}' does not exist or upload metadata is missing.")

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                saved_filename = data.get("saved_filename")
                if not saved_filename:
                    raise KeyError("Field 'saved_filename' is missing in metadata.")
                return saved_filename
        except (json.JSONDecodeError, KeyError, OSError) as e:
            raise RuntimeError(f"Failed to read metadata for job '{safe_job_id}': {str(e)}")
