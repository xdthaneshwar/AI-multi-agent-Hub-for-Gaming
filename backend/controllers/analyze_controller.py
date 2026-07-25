from fastapi import HTTPException
from backend.services.video_service import VideoService

class AnalyzeController:
    """
    AnalyzeController processes incoming analysis requests, coordinates
    the VideoService execution, and handles exceptions gracefully.
    """

    def __init__(self):
        self.video_service = VideoService()

    def run_analysis(self, filename: str) -> dict:
        """
        Coordinates the analysis of a specific video file.

        Args:
            filename (str): Name of the video file to analyze.

        Returns:
            dict: JSON-serializable response dict with status and analysis metadata.
        """
        try:
            # Execute analysis pipeline using VideoService
            analysis_data = self.video_service.analyze_video_file(filename)
            
            return {
                "success": True,
                "filename": filename,
                "analysis": analysis_data
            }
        except FileNotFoundError as e:
            # Respond with 404 if the video is missing
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
