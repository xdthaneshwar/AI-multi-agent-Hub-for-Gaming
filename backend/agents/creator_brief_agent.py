class RuleBasedBriefGenerator:
    """
    Implements rule-based logic to generate a human-readable creator brief summary
    based on video analysis, highlights, SEO, and thumbnail metadata.
    """

    def generate_summary(
        self, 
        analysis: dict, 
        highlights: list, 
        seo: dict, 
        thumbnails: list
    ) -> str:
        """
        Generates a concise creator brief summary string.

        Args:
            analysis (dict): Video metadata analysis.
            highlights (list): List of detected highlight objects.
            seo (dict): SEO metadata dictionary.
            thumbnails (list): List of generated thumbnail objects.

        Returns:
            str: Human-readable summary paragraph outlining duration, highlights,
                 thumbnails, and publishing strategy.
        """
        duration = analysis.get("duration", 0.0)
        num_highlights = len(highlights) if isinstance(highlights, list) else 0
        num_thumbnails = len(thumbnails) if isinstance(thumbnails, list) else 0

        width = analysis.get("width", 0)
        height = analysis.get("height", 0)
        is_vertical = height > width or duration < 60.0

        if is_vertical:
            strategy = (
                "Optimal for short-form video platforms (YouTube Shorts, TikTok, Instagram Reels). "
                "Leverage energetic visual thumbnails and brief high-paced clips for maximum engagement."
            )
        else:
            strategy = (
                "Optimal for long-form video platforms (YouTube, Twitch VODs). "
                "Include the detected highlight timestamps as chapter marks in the video description."
            )

        summary = (
            f"Video Summary:\n"
            f"- Total Duration: {duration:.2f} seconds\n"
            f"- Key Highlights Detected: {num_highlights} action moments\n"
            f"- Preview Thumbnails Generated: {num_thumbnails} candidate frames\n\n"
            f"Publishing Strategy:\n"
            f"{strategy}"
        )
        return summary


class CreatorBriefAgent:
    """
    CreatorBriefAgent compiles video analysis, highlights, SEO, and thumbnails
    into a unified creator brief report.
    It delegates summary generation to a strategy (rule-based or LLM-based).
    """

    def __init__(self, summary_generator=None):
        # Dependency Injection / Strategy Pattern for future LLM extensibility
        self.summary_generator = summary_generator or RuleBasedBriefGenerator()

    def generate_brief(
        self, 
        analysis: dict, 
        highlights: list, 
        seo: dict, 
        thumbnails: list
    ) -> dict:
        """
        Combines all component outputs into a single structured creator brief.

        Args:
            analysis (dict): Video analysis dictionary.
            highlights (list): Detected highlights list.
            seo (dict): SEO title, description, tags, hashtags.
            thumbnails (list): Thumbnails metadata list.

        Returns:
            dict: Complete creator brief dictionary.
        """
        summary_text = self.summary_generator.generate_summary(
            analysis=analysis,
            highlights=highlights,
            seo=seo,
            thumbnails=thumbnails
        )

        return {
            "summary": summary_text,
            "video_analysis": analysis,
            "seo": seo,
            "highlights": highlights,
            "thumbnails": thumbnails
        }
