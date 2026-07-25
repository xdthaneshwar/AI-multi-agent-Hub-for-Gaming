from pathlib import Path
from agents.highlight_agent import HighlightAgent
from backend.config import UPLOAD_DIR

class HighlightService:
    """
    HighlightService coordinates highlight detection operations,
    connecting the controllers to the core HighlightAgent.
    """

    def __init__(self):
        self.highlight_agent = HighlightAgent()

    def detect_video_highlights(
        self, 
        filename: str, 
        motion_threshold: float, 
        cooldown_seconds: float
    ) -> list:
        """
        Validates the video file existence and triggers highlight detection.

        Args:
            filename (str): The filename of the uploaded gaming video.
            motion_threshold (float): Threshold percentage of pixel differences.
            cooldown_seconds (float): Delay in seconds before another highlight can be flagged.

        Returns:
            list: List of detected highlights with timestamps.
        """
        # Sanitize filename to prevent directory traversal
        safe_filename = Path(filename).name
        video_path = UPLOAD_DIR / safe_filename

        # Ensure the file exists before invoking the agent
        if not video_path.exists():
            raise FileNotFoundError(f"Video file '{safe_filename}' not found in uploads folder.")

        # Run the detection algorithm
        return self.highlight_agent.detect_highlights(
            video_path=str(video_path),
            motion_threshold=motion_threshold,
            cooldown_seconds=cooldown_seconds
        )
