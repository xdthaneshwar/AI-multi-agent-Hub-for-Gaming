import uuid
import shutil
import json
from fastapi import UploadFile
from backend.config import UPLOAD_DIR, RESULTS_DIR
from backend.services.job_service import JobService
from backend.services.video_service import VideoService
from backend.services.highlight_service import HighlightService

# Instantiate JobService to manage job metadata records
job_service = JobService()

def save_uploaded_video(file: UploadFile):
    """
    Saves an uploaded video file to the 'uploads' directory, registers job metadata,
    and automatically triggers analysis and highlight detection synchronously.

    Args:
        file (UploadFile): The uploaded video file from FastAPI.

    Returns:
        dict: A dictionary containing success status, job ID, filename, and message.
    """
    # Ensure the uploads directory exists at the root (creates it if missing)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate a unique job ID (UUID)
    job_id = str(uuid.uuid4())

    # Create a unique filename using job_id and the original file name to prevent overwrites
    original_filename = file.filename
    saved_filename = f"{job_id}_{original_filename}"
    file_path = UPLOAD_DIR / saved_filename

    # Save the file stream to the target location
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Register upload metadata with JobService (creates results/<job_id>/upload.json)
    job_service.create_job_metadata(
        job_id=job_id,
        original_filename=original_filename,
        saved_filename=saved_filename
    )

    job_results_dir = RESULTS_DIR / job_id

    # Automatically trigger analysis instantly on upload
    try:
        video_service = VideoService()
        analysis_data = video_service.analyze_video_file(saved_filename)
        
        # Save analysis result to results/<job_id>/analysis.json
        analysis_file_path = job_results_dir / "analysis.json"
        with open(analysis_file_path, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=4)
    except Exception as e:
        print(f"Auto-analysis failed on upload: {e}")

    # Automatically trigger highlight detection instantly on upload (using default threshold=8.0, cooldown=3.0)
    try:
        highlight_service = HighlightService()
        highlights_data = highlight_service.detect_video_highlights(
            filename=saved_filename,
            motion_threshold=8.0,
            cooldown_seconds=3.0
        )
        
        # Save highlights result to results/<job_id>/highlights.json
        highlights_file_path = job_results_dir / "highlights.json"
        with open(highlights_file_path, "w", encoding="utf-8") as f:
            json.dump(highlights_data, f, indent=4)
    except Exception as e:
        print(f"Auto-highlight detection failed on upload: {e}")

    return {
        "success": True,
        "job_id": job_id,
        "filename": saved_filename,
        "message": "Video uploaded successfully"
    }
