import json
from pathlib import Path
from fastapi import HTTPException
from backend.services.video_service import VideoService
from backend.services.job_service import JobService
from backend.config import RESULTS_DIR

class AnalyzeController:
    """
    AnalyzeController processes incoming analysis requests by resolving
    job IDs to filenames, running the video service, and returning results.
    It checks for pre-analyzed metadata in results/ first to return fast.
    """

    def __init__(self):
        self.video_service = VideoService()
        self.job_service = JobService()

    def run_analysis(self, job_id: str) -> dict:
        """
        Coordinates the analysis of a specific video file using a job ID.

        Args:
            job_id (str): Unique identifier of the upload job (or placeholder).

        Returns:
            dict: JSON-serializable response dict with status and analysis metadata.
        """
        try:
            # 1. Resolve job_id (handles default placeholders and latest job retrieval)
            resolved_job_id = self.job_service.resolve_job_id(job_id)
            
            # 2. Setup path checks
            safe_job_id = Path(resolved_job_id).name
            job_results_dir = RESULTS_DIR / safe_job_id
            analysis_file = job_results_dir / "analysis.json"

            # 3. Check if pre-calculated analysis exists to return instantly
            if analysis_file.exists():
                try:
                    with open(analysis_file, "r", encoding="utf-8") as f:
                        analysis_data = json.load(f)
                    return {
                        "success": True,
                        "job_id": resolved_job_id,
                        "analysis": analysis_data
                    }
                except Exception:
                    pass  # Fallback to recalculation if JSON is corrupt

            # 4. Resolve job_id to filename using JobService
            filename = self.job_service.get_saved_filename(resolved_job_id)

            # 5. Execute analysis pipeline using VideoService
            analysis_data = self.video_service.analyze_video_file(filename)
            
            # Save the calculated analysis for subsequent calls
            job_results_dir.mkdir(parents=True, exist_ok=True)
            with open(analysis_file, "w", encoding="utf-8") as f:
                json.dump(analysis_data, f, indent=4)

            return {
                "success": True,
                "job_id": resolved_job_id,
                "analysis": analysis_data
            }
        except FileNotFoundError as e:
            # Respond with 404 if upload.json or the video is missing
            raise HTTPException(status_code=404, detail=str(e))
        except RuntimeError as e:
            # Respond with 400 Bad Request if media processing fails
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # Handle fallback unexpected internal exceptions
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred during video analysis: {str(e)}"
            )
