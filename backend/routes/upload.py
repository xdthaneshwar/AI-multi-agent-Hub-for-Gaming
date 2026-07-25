from fastapi import APIRouter, File, UploadFile
from backend.controllers import upload_controller

# Create the APIRouter with Swagger tags to group endpoints in '/docs'
router = APIRouter(tags=["Upload"])

@router.post("/upload")
def upload_video(file: UploadFile = File(...)):
    """
    Endpoint to upload a gaming video.

    Accepts a video file from a multipart form upload and saves it locally.
    """
    # Delegate the file saving and job generation logic to the controller
    return upload_controller.save_uploaded_video(file)
