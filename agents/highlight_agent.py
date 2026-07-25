import cv2
from pathlib import Path

class HighlightAgent:
    """
    The Highlight Agent analyzes video files frame-by-frame using OpenCV.
    It performs frame differencing to identify high-motion events (such as action gameplay,
    explosions, or rapid visual shifts) and records their timestamps.
    """

    def detect_highlights(
        self, 
        video_path: str, 
        motion_threshold: float = 8.0, 
        cooldown_seconds: float = 3.0
    ) -> list:
        """
        Processes a video file to detect high-motion highlights.

        Args:
            video_path (str): The absolute path to the video file.
            motion_threshold (float): The percentage of pixels changed to trigger a highlight (e.g. 8.0%).
            cooldown_seconds (float): Time in seconds to wait before detecting another highlight.

        Returns:
            list: List of dictionaries containing highlight timestamp, frame index, and motion score.
        """
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            raise RuntimeError("OpenCV could not open the video file.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0  # Fallback FPS if unable to read from metadata

        highlights = []
        prev_gray = None
        last_highlight_time = -cooldown_seconds  # Set to negative cooldown so the first event triggers immediately

        # Downscale dimensions to accelerate frame differencing calculations (e.g., 320x180)
        # This prevents high-resolution videos from causing high CPU load.
        processing_width = 320
        processing_height = 180
        total_pixels = processing_width * processing_height

        frame_idx = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Preprocess frame (resize, gray, blur)
                gray_blurred = self._preprocess_frame(frame, processing_width, processing_height)

                # Initialize on the first frame and continue
                if prev_gray is None:
                    prev_gray = gray_blurred
                    frame_idx += 1
                    continue

                # Measure motion intensity (percentage of active pixels relative to the whole frame)
                motion_intensity = self._calculate_motion_intensity(prev_gray, gray_blurred, total_pixels)

                # Check if motion intensity exceeds threshold and respects cooldown
                current_time_seconds = frame_idx / fps
                if motion_intensity >= motion_threshold:
                    time_since_last_highlight = current_time_seconds - last_highlight_time
                    if time_since_last_highlight >= cooldown_seconds:
                        timestamp = self._seconds_to_timestamp(current_time_seconds)
                        highlights.append({
                            "timestamp": timestamp,
                            "time_seconds": round(current_time_seconds, 2),
                            "frame_index": frame_idx,
                            "motion_intensity": round(motion_intensity, 2)
                        })
                        last_highlight_time = current_time_seconds

                # Set current frame as previous for next loop
                prev_gray = gray_blurred
                frame_idx += 1

        finally:
            cap.release()  # Always release OpenCV resources

        return highlights

    def _preprocess_frame(self, frame, width: int, height: int):
        """
        Resizes frame, converts it to grayscale, and applies blur to remove noise.
        """
        resized = cv2.resize(frame, (width, height))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        return cv2.GaussianBlur(gray, (21, 21), 0)

    def _calculate_motion_intensity(self, prev_frame, curr_frame, total_pixels: int) -> float:
        """
        Calculates the percentage difference of moving pixels between two frames.
        """
        frame_delta = cv2.absdiff(prev_frame, curr_frame)
        _, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
        non_zero_pixels = cv2.countNonZero(thresh)
        return (non_zero_pixels / total_pixels) * 100

    def _seconds_to_timestamp(self, total_seconds: float) -> str:
        """
        Converts a time duration in seconds into HH:MM:SS format.

        Args:
            total_seconds (float): Total seconds to convert.

        Returns:
            str: Formatted timestamp string (HH:MM:SS).
        """
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
