import uuid
import shutil
import json
from fastapi import UploadFile
from backend.config import UPLOAD_DIR, RESULTS_DIR

def save_uploaded_video(file: UploadFile):
    """
    Saves an uploaded video file to the 'uploads' directory.
    Generates a unique job ID for tracking purposes.

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

    # Save the upload details inside results/<job_id>/upload.json
    job_results_dir = RESULTS_DIR / job_id
    job_results_dir.mkdir(parents=True, exist_ok=True)

    upload_metadata = {
        "job_id": job_id,
        "original_filename": original_filename,
        "saved_filename": saved_filename
    }

    metadata_file_path = job_results_dir / "upload.json"
    with open(metadata_file_path, "w", encoding="utf-8") as f:
        json.dump(upload_metadata, f, indent=4)

    return {
        "success": True,
        "job_id": job_id,
        "filename": saved_filename,
        "message": "Video uploaded successfully"
    }
