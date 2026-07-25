import uuid
import shutil
from fastapi import UploadFile
from backend.config import UPLOAD_DIR
from backend.services.job_service import JobService

# Instantiate JobService to manage job metadata records
job_service = JobService()


def save_uploaded_video(file: UploadFile):
    """
    Saves an uploaded video file to the 'uploads' directory and
    registers upload metadata.

    This endpoint ONLY uploads the video.
    Analysis and Highlight detection are executed separately
    through their dedicated APIs.
    """

    # Ensure uploads directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate a unique job ID
    job_id = str(uuid.uuid4())

    # Create a unique filename
    original_filename = file.filename
    saved_filename = f"{job_id}_{original_filename}"

    file_path = UPLOAD_DIR / saved_filename

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save upload metadata
    job_service.create_job_metadata(
        job_id=job_id,
        original_filename=original_filename,
        saved_filename=saved_filename
    )

    return {
        "success": True,
        "job_id": job_id,
        "filename": saved_filename,
        "message": "Video uploaded successfully"
    }