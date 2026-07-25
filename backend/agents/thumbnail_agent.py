import cv2
from pathlib import Path

class ThumbnailAgent:
    """
    The Thumbnail Agent extracts preview frames (thumbnails) from a video 
    at specific highlight timestamps using OpenCV.
    """

    def extract_thumbnails(self, video_path: str, highlights: list, output_dir: Path) -> list:
        """
        Extracts thumbnail images from highlight timestamps and saves them.
        If highlights list has fewer than 3 items, falls back to evenly spaced 
        intervals (10%, 50%, 90% of duration) so 3 options are always generated.

        Args:
            video_path (str): Path to the video file.
            highlights (list): List of highlight dictionaries.
            output_dir (Path): Target directory to save thumbnails.

        Returns:
            list: List of dicts containing timestamp and relative image path.
        """
        video_file = Path(video_path)
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(video_file))
        if not cap.isOpened():
            raise RuntimeError("OpenCV could not open the video file.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if fps <= 0:
            fps = 30.0

        candidates = []  # Holds tuples of (frame_index, timestamp_str)

        # 1. Sort highlights by motion intensity (descending) to choose the best action frames
        sorted_highlights = sorted(
            highlights, 
            key=lambda x: x.get("motion_intensity", 0.0), 
            reverse=True
        )

        for h in sorted_highlights[:3]:
            frame_idx = h.get("frame_index")
            timestamp = h.get("timestamp", "00:00:00")
            if frame_idx is not None and 0 <= frame_idx < total_frames:
                candidates.append((frame_idx, timestamp))

        # 2. Fallback: Supplement with evenly spaced frames if highlights count < 3
        if len(candidates) < 3 and total_frames > 0:
            intervals = [0.1, 0.5, 0.9]  # 10%, 50%, 90% of video
            for ratio in intervals:
                if len(candidates) >= 3:
                    break
                frame_idx = int(total_frames * ratio)
                # Avoid duplicate frames near already selected timestamps (e.g. within 2 seconds)
                if any(abs(c[0] - frame_idx) < (fps * 2) for c in candidates):
                    continue
                time_seconds = frame_idx / fps
                timestamp = self._seconds_to_timestamp(time_seconds)
                candidates.append((frame_idx, timestamp))

        # 3. Extract and save the target frames
        extracted_thumbnails = []
        try:
            for idx, (frame_idx, timestamp) in enumerate(candidates, start=1):
                # Seek to target frame position
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    continue

                filename = f"thumbnail_{idx}.jpg"
                file_path = output_dir / filename

                # Write frame to file as JPEG
                # cv2.imwrite returns False on failure (e.g. bad path, disk full)
                # without raising an exception, so we check explicitly
                success = cv2.imwrite(str(file_path), frame)
                if not success:
                    raise RuntimeError(f"OpenCV failed to write thumbnail to: {file_path}")

                # Relative path as requested (e.g., uploads/thumbnails/<job_id>/thumbnail_X.jpg)
                relative_path = f"uploads/thumbnails/{output_dir.name}/{filename}"

                extracted_thumbnails.append({
                    "timestamp": timestamp,
                    "image_path": relative_path
                })
        finally:
            cap.release()

        return extracted_thumbnails

    def _seconds_to_timestamp(self, total_seconds: float) -> str:
        """
        Converts seconds to HH:MM:SS format.
        """
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
