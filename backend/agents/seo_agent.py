import re
from pathlib import Path

class RuleBasedSEOGenerator:
    """
    Implements rule-based logic to generate SEO titles, descriptions,
    tags, and hashtags based on video metadata and the original filename.
    """

    def generate(self, original_filename: str, metadata: dict) -> dict:
        """
        Generates SEO metadata based on original file name and video details.

        Args:
            original_filename (str): The user's original uploaded filename.
            metadata (dict): Technical video analysis dictionary.

        Returns:
            dict: SEO title, description, tags, and hashtags.
        """
        # 1. Clean the filename to extract clean title
        # Remove extension
        clean_title = Path(original_filename).stem
        # Replace common separators with spaces
        clean_title = re.sub(r'[-_]+', ' ', clean_title)
        # Remove multiple spaces
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        # Capitalize words to Title Case
        clean_title = clean_title.title()

        # 2. Extract technical metrics
        duration = metadata.get("duration", 0.0)
        resolution = metadata.get("resolution", "Unknown")
        fps = metadata.get("fps", 0.0)

        # 3. Determine format (is it a short vertical video like YouTube Shorts or Reels?)
        width = metadata.get("width", 0)
        height = metadata.get("height", 0)
        is_vertical = height > width or duration < 60.0

        # 4. Generate Title
        if is_vertical:
            seo_title = f"{clean_title} #shorts"
        else:
            seo_title = f"{clean_title} | Epic Gameplay Highlight"

        # 5. Generate Description
        description = (
            f"Watch this amazing gameplay video: {clean_title}!\n\n"
            f"🎥 Video Specifications:\n"
            f"- Resolution: {resolution}\n"
            f"- FPS: {fps}\n"
            f"- Duration: {duration} seconds\n\n"
            f"If you enjoyed the video, make sure to drop a like and subscribe for more action-packed gaming moments!"
        )

        # 6. Generate Tags (combination of title keywords and general gaming terms)
        title_keywords = [w.lower() for w in clean_title.split() if len(w) > 3]
        base_tags = ["gaming", "gameplay", "gamer", "highlights", "gaming hub"]
        if is_vertical:
            base_tags.extend(["shorts", "youtube shorts", "shorts feed"])
        tags = list(set(base_tags + title_keywords))

        # 7. Generate Hashtags
        hashtags = ["#gaming", "#gamer", "#gameplay", "#viral"]
        if is_vertical:
            hashtags.extend(["#shorts", "#shortsvideo", "#shortsfeed"])

        return {
            "title": seo_title,
            "description": description,
            "tags": tags,
            "hashtags": hashtags
        }

class SEOAgent:
    """
    SEOAgent generates optimized metadata (titles, descriptions, tags) for videos.
    It delegates to a generator strategy, which can be rule-based or LLM-based in the future.
    """

    def __init__(self, generator=None):
        # Allow passing a custom generator strategy for extensibility (SOLID)
        self.generator = generator or RuleBasedSEOGenerator()

    def generate_seo(self, original_filename: str, metadata: dict) -> dict:
        """
        Generates SEO content using the configured generator strategy.

        Args:
            original_filename (str): The original video filename.
            metadata (dict): The technical metadata of the video.

        Returns:
            dict: Structured SEO properties dictionary.
        """
        return self.generator.generate(original_filename, metadata)
