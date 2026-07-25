import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile

# Define the path to the 'uploads' directory at the project root using pathlib.Path
# __file__ points to: backend/controllers/upload_controller.py
# .resolve().parents[2] navigates 3 levels up to: AI-multi-agent-Hub-for-Gaming/
BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"

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
    # Note: We use synchronous file writing here because disk write operations are blocking.
    # FastAPI handles regular synchronous 'def' endpoints/functions in an external thread pool
    # so it does not block the main asynchronous event loop.
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "job_id": job_id,
        "filename": saved_filename,
        "message": "Video uploaded successfully"
    }
