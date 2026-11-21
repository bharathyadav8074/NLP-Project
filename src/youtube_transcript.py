from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi


def get_video_id(url: str) -> str:
    """Extract a YouTube video ID from common YouTube URL formats."""

    parsed = urlparse(url)
    host = parsed.netloc.lower().replace("www.", "")
    video_id = None

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]

    elif host in {
        "youtube.com",
        "m.youtube.com",
        "music.youtube.com"
    }:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]

        elif parsed.path.startswith(("/embed/", "/shorts/")):
            parts = parsed.path.strip("/").split("/")
            video_id = parts[1] if len(parts) > 1 else None

    if not video_id or len(video_id) != 11:
        raise ValueError("Please enter a valid YouTube video URL.")

    return video_id


def fetch_transcript(video_id: str, language: str = "en"):
    """Fetch and normalize YouTube transcript segments."""

    try:
        transcript = YouTubeTranscriptApi().fetch(
            video_id,
            languages=[language]
        )

    except Exception as exc:
        raise RuntimeError(
            f"Could not fetch transcript in '{language}'. "
            "The video may have captions disabled, "
            "the language may be unavailable, or YouTube "
            "may have temporarily blocked the request. "
            f"Details: {exc}"
        ) from exc

    cleaned = []

    for row in transcript:

        text = " ".join(str(row.text).split())

        if text:
            cleaned.append({
                "text": text,
                "start": float(row.start),
                "duration": float(row.duration)
            })

    return cleaned