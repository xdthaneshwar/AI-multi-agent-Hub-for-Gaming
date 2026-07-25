import cv2
import numpy as np
from pathlib import Path

class ThumbnailAgent:
    """
    Refactored Production-Grade Thumbnail Curator Agent for AI Multi-Agent Hub for Gaming.
    
    Fast, reliable, and bug-free image quality ranking engine optimized for gaming thumbnails.
    Evaluates 6 essential visual metrics (Sharpness, Brightness, Contrast, Saturation, Edge Density, Color Richness)
    across a ±20 frame window around highlights.
    """

    def extract_thumbnails(self, video_path: str, highlights: list, output_dir: Path) -> list:
        """
        Extracts high-quality thumbnail candidate previews for a video job.

        Args:
            video_path (str): Absolute path to the video file.
            highlights (list): List of highlight metadata dicts.
            output_dir (Path): Output directory to save thumbnails.

        Returns:
            list: List of dicts with 'timestamp', 'image_path', 'quality_score', and 'selection_reason'.
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

        target_center_frames = []

        # Sort highlights by motion intensity descending to prioritize action moments
        sorted_highlights = sorted(
            highlights, 
            key=lambda x: x.get("motion_intensity", 0.0), 
            reverse=True
        )

        # 1. Select center highlights ensuring centers are at least 2 seconds apart
        for h in sorted_highlights:
            if len(target_center_frames) >= 5:
                break
            frame_idx = h.get("frame_index")
            timestamp = h.get("timestamp", "00:00:00")
            if frame_idx is not None and 0 <= frame_idx < total_frames:
                if not any(abs(c[0] - frame_idx) < (fps * 2) for c in target_center_frames):
                    target_center_frames.append((frame_idx, timestamp))

        # 2. Supplement with evenly spaced intervals if target centers < 3
        if len(target_center_frames) < 3 and total_frames > 0:
            intervals = [0.1, 0.3, 0.5, 0.7, 0.9]
            for ratio in intervals:
                if len(target_center_frames) >= 5:
                    break
                frame_idx = int(total_frames * ratio)
                if any(abs(c[0] - frame_idx) < (fps * 2) for c in target_center_frames):
                    continue
                time_seconds = frame_idx / fps
                timestamp = self._seconds_to_timestamp(time_seconds)
                target_center_frames.append((frame_idx, timestamp))

        all_candidates = []

        try:
            # Search ±20 frame window around each highlight center
            for center_frame_idx, default_timestamp in target_center_frames:
                start_frame = max(0, center_frame_idx - 20)
                end_frame = min(total_frames - 1, center_frame_idx + 20)

                # Seek once per window and read sequentially for maximum speed
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

                for candidate_idx in range(start_frame, end_frame + 1):
                    ret, full_frame = cap.read()
                    if not ret or full_frame is None or full_frame.size == 0:
                        break

                    # Stride by 2: evaluate every second frame in the ±20 window
                    if (candidate_idx - start_frame) % 2 != 0:
                        continue

                    # Downscale copy to 480p height for fast metric calculation
                    h_orig, w_orig = full_frame.shape[:2]
                    if h_orig > 480:
                        scale = 480.0 / h_orig
                        analysis_frame = cv2.resize(full_frame, (int(w_orig * scale), 480))
                    else:
                        analysis_frame = full_frame

                    # Evaluate 6 essential metrics & hard rejection check
                    metrics = self._compute_metrics(analysis_frame)
                    if self._is_hard_rejected(metrics):
                        continue

                    quality_score, reasons = self._score_candidate(metrics)
                    time_sec = candidate_idx / fps
                    timestamp_str = self._seconds_to_timestamp(time_sec)

                    all_candidates.append({
                        "frame": full_frame,  # Keep uncompressed high-res original for saving
                        "frame_index": candidate_idx,
                        "timestamp": timestamp_str,
                        "quality_score": quality_score,
                        "selection_reason": reasons,
                        "hsv_hist": self._compute_hsv_histogram(analysis_frame)
                    })

        finally:
            cap.release()

        if not all_candidates:
            # Fallback to first frame if all candidates were hard rejected
            cap = cv2.VideoCapture(str(video_file))
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None and frame.size > 0:
                all_candidates.append({
                    "frame": frame,
                    "frame_index": 0,
                    "timestamp": "00:00:00",
                    "quality_score": 50.0,
                    "selection_reason": ["Default fallback frame"],
                    "hsv_hist": None
                })

        # Rank and select top 3 diverse candidates
        selected_candidates = self._select_diverse_top3(all_candidates, min_frame_gap=int(fps * 2), fps=fps)

        extracted_thumbnails = []
        for idx, candidate in enumerate(selected_candidates, start=1):
            best_frame = candidate["frame"]
            best_score = candidate["quality_score"]
            timestamp_str = candidate["timestamp"]
            reasons = candidate["selection_reason"]

            filename = f"thumbnail_{idx}.jpg"
            file_path = output_dir / filename

            # Write high-quality JPEG
            success = cv2.imwrite(str(file_path), best_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            if not success:
                raise RuntimeError(f"OpenCV failed to write thumbnail to: {file_path}")

            relative_path = f"uploads/thumbnails/{output_dir.name}/{filename}"

            extracted_thumbnails.append({
                "timestamp": timestamp_str,
                "image_path": relative_path,
                "quality_score": best_score,
                "selection_reason": reasons
            })

        return extracted_thumbnails

    def _compute_metrics(self, frame: np.ndarray) -> dict:
        """
        Calculates the 6 essential computer vision visual metrics.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, w = gray.shape

        # 1. Sharpness (Variance of Laplacian)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # 2. Brightness (Mean grayscale intensity)
        brightness = float(np.mean(gray))

        # 3. Contrast (Standard deviation of intensity)
        contrast = float(np.std(gray))

        # 4. Saturation (Mean S channel in HSV)
        saturation = float(np.mean(hsv[:, :, 1]))

        # 5. Edge Density (Canny edge pixel ratio)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = float(np.count_nonzero(edges) / float(h * w))

        # 6. Color Richness (Hasler & Süsstrunk metric)
        b, g, r = cv2.split(frame.astype("float"))
        rg = np.abs(r - g)
        yb = np.abs(0.5 * (r + g) - b)
        std_root = np.sqrt(np.std(rg)**2 + np.std(yb)**2)
        mean_root = np.sqrt(np.mean(rg)**2 + np.mean(yb)**2)
        color_richness = float(std_root + 0.3 * mean_root)

        return {
            "sharpness": sharpness,
            "brightness": brightness,
            "contrast": contrast,
            "saturation": saturation,
            "edge_density": edge_density,
            "color_richness": color_richness
        }

    def _is_hard_rejected(self, metrics: dict) -> bool:
        """
        Evaluates hard rejection threshold limits to discard poor frames.
        """
        if metrics["brightness"] < 20.0 or metrics["brightness"] > 240.0:
            return True
        if metrics["sharpness"] < 35.0:
            return True
        if metrics["contrast"] < 12.0:
            return True
        if metrics["edge_density"] < 0.008:
            return True
        return False

    def _score_candidate(self, metrics: dict) -> tuple[float, list]:
        """
        Normalizes retained metrics and calculates composite Quality Score (0.0 to 100.0).
        """
        n_sharpness = min(metrics["sharpness"] / 550.0, 1.0)
        n_brightness = max(0.0, 1.0 - (abs(metrics["brightness"] - 120.0) / 120.0))
        n_contrast = min(metrics["contrast"] / 75.0, 1.0)
        n_saturation = min(metrics["saturation"] / 180.0, 1.0)
        n_edge_density = min(metrics["edge_density"] / 0.15, 1.0)
        n_color_richness = min(metrics["color_richness"] / 80.0, 1.0)

        # Weighted combination:
        # Sharpness: 30%, Color Richness: 20%, Saturation: 15%, Contrast: 15%, Edge Density: 10%, Brightness: 10%
        composite = (
            0.30 * n_sharpness +
            0.20 * n_color_richness +
            0.15 * n_saturation +
            0.15 * n_contrast +
            0.10 * n_edge_density +
            0.10 * n_brightness
        ) * 100.0

        quality_score = round(max(0.0, min(100.0, composite)), 1)

        reasons = []
        if n_sharpness >= 0.60:
            reasons.append("Excellent sharpness")
        if n_contrast >= 0.60:
            reasons.append("Strong colour contrast")
        if n_color_richness >= 0.60 or n_saturation >= 0.60:
            reasons.append("Vibrant color palette")
        if n_edge_density >= 0.50:
            reasons.append("High detail")

        if not reasons:
            reasons.append("Clear visual focus")

        return quality_score, reasons

    def _compute_hsv_histogram(self, frame: np.ndarray) -> np.ndarray:
        """Computes a normalized HSV color histogram for frame similarity checking."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [18, 25], [0, 180, 0, 256])
        cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        return hist

    def _select_diverse_top3(self, candidates: list, min_frame_gap: int, fps: float = 30.0) -> list:
        """
        Ranks candidate frames and selects top 3 candidates that are visually distinct
        and separated by at least min_frame_gap frames.
        """
        candidates_sorted = sorted(candidates, key=lambda c: c["quality_score"], reverse=True)

        selected = []
        # Track immutable frame_index primitives instead of comparing candidate dicts directly
        selected_indices = set()

        for candidate in candidates_sorted:
            if len(selected) >= 3:
                break

            idx = candidate["frame_index"]

            # 1. Strict temporal gap check (at least 2 seconds apart)
            if any(abs(idx - s_idx) < min_frame_gap for s_idx in selected_indices):
                continue

            # 2. Perceptual visual histogram correlation check (must be visually distinct)
            is_duplicate = False
            if candidate["hsv_hist"] is not None:
                for sel in selected:
                    if sel["hsv_hist"] is not None:
                        sim = cv2.compareHist(candidate["hsv_hist"], sel["hsv_hist"], cv2.HISTCMP_CORREL)
                        if sim > 0.88:
                            is_duplicate = True
                            break
            if is_duplicate:
                continue

            selected.append(candidate)
            selected_indices.add(idx)

        # Fallback 1: Enforce at least 1 second temporal gap if 3 unique candidates weren't selected
        if len(selected) < 3:
            min_gap_relaxed = int(fps * 1.0)
            for candidate in candidates_sorted:
                if len(selected) >= 3:
                    break
                idx = candidate["frame_index"]
                if idx not in selected_indices:
                    if not any(abs(idx - s_idx) < min_gap_relaxed for s_idx in selected_indices):
                        selected.append(candidate)
                        selected_indices.add(idx)

        # Fallback 2: Final fallback if total frames in video are very short
        if len(selected) < 3:
            for candidate in candidates_sorted:
                if len(selected) >= 3:
                    break
                idx = candidate["frame_index"]
                if idx not in selected_indices:
                    selected.append(candidate)
                    selected_indices.add(idx)

        # Sort selected 3 by original frame timeline order
        return sorted(selected, key=lambda c: c["frame_index"])

    def _seconds_to_timestamp(self, total_seconds: float) -> str:
        """Converts total seconds into HH:MM:SS timestamp string."""
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
