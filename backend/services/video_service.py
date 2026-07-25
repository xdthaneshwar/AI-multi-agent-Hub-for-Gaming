from pathlib import Path
from agents.analyze_agent import AnalyzeAgent
from backend.config import UPLOAD_DIR


class VideoService:
    """
    VideoService coordinates backend operations related to video manipulation,
    bridging controllers with external processing agents.
    """

    def __init__(self):
        self.analyze_agent = AnalyzeAgent()

    def analyze_video_file(self, filename: str) -> dict:
        """
        Validates the video file existence and triggers the AnalyzeAgent.

        Args:
            filename (str): The filename of the uploaded video.

        Returns:
            dict: Extracted video metadata dictionary.
        """
        # Sanitize input path to prevent directory traversal vulnerabilities
        safe_filename = Path(filename).name
        video_path = UPLOAD_DIR / safe_filename

        # Ensure the file exists in the uploads directory
        if not video_path.exists():
            raise FileNotFoundError(f"Video file '{safe_filename}' not found in uploads folder.")

        # Trigger analysis via the AnalyzeAgent
        return self.analyze_agent.analyze_video(str(video_path))
