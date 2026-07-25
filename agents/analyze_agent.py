import cv2
from pathlib import Path
from moviepy import VideoFileClip

class AnalyzeAgent:
    """
    The Analyze Agent uses OpenCV and MoviePy to inspect video files
    and extract detailed technical metadata (duration, FPS, resolution, etc.).
    """

    def analyze_video(self, video_path: str) -> dict:
        """
        Inspects the video at the given path and returns its technical metadata.

        Args:
            video_path (str): The absolute path to the video file.

        Returns:
            dict: A dictionary containing duration, fps, frame_count, width,
                  height, resolution, file_size, and video_format.
        """
        file_path = Path(video_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        # Get filesystem properties
        file_size = file_path.stat().st_size
        video_format = file_path.suffix

        # Get properties from specialized media processors
        duration = self._get_video_duration(file_path)
        opencv_data = self._get_opencv_properties(file_path)

        return {
            "duration": duration,
            "fps": opencv_data["fps"],
            "frame_count": opencv_data["frame_count"],
            "width": opencv_data["width"],
            "height": opencv_data["height"],
            "resolution": opencv_data["resolution"],
            "file_size": file_size,
            "video_format": video_format
        }

    def _get_video_duration(self, file_path: Path) -> float:
        """
        Uses MoviePy to read the exact video duration.

        Args:
            file_path (Path): Path to the video file.

        Returns:
            float: Duration in seconds rounded to 2 decimal places.
        """
        clip = None
        try:
            clip = VideoFileClip(str(file_path))
            return round(float(clip.duration), 2)
        except Exception as e:
            raise RuntimeError(f"MoviePy failed to retrieve video duration: {str(e)}")
        finally:
            if clip is not None:
                clip.close()  # Close file reader to release lock

    def _get_opencv_properties(self, file_path: Path) -> dict:
        """
        Uses OpenCV to capture and parse properties from video streams.

        Args:
            file_path (Path): Path to the video file.

        Returns:
            dict: Dictionary of fps, frame_count, width, height, and resolution.
        """
        try:
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                raise RuntimeError("OpenCV failed to open the video file.")

            fps = float(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()  # Release resource

            return {
                "fps": round(fps, 2),
                "frame_count": frame_count,
                "width": width,
                "height": height,
                "resolution": f"{width}x{height}"
            }
        except Exception as e:
            raise RuntimeError(f"OpenCV failed to parse video properties: {str(e)}")

