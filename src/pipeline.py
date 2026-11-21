import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

STOPWORDS = {
    "the","a","an","and","or","but","if","then","so","to","of","in","on","for","with",
    "is","are","was","were","be","been","being","it","this","that","these","those","we",
    "you","they","i","he","she","as","at","by","from","about","into","there","here",
    "have","has","had","do","does","did","will","would","can","could","should","not",
    "your","our","their","what","when","where","why","how","which","who","also"
}

def format_timestamp(seconds):
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def make_time_chunks(transcript, chunk_seconds=75):
    """Group transcript segments into approximately equal time windows."""
    if not transcript:
        return []
    chunks, current, start = [], [], transcript[0]["start"]
    for segment in transcript:
        if current and segment["start"] - start >= chunk_seconds:
            chunks.append({"start": start, "text": " ".join(x["text"] for x in current)})
            current, start = [], segment["start"]
        current.append(segment)
    if current:
        chunks.append({"start": start, "text": " ".join(x["text"] for x in current)})
    return [c for c in chunks if c["text"].strip()]


def _topic_boundaries(chunks, sensitivity):
    """Find topic shifts using cosine distance between adjacent TF-IDF chunks."""
    if len(chunks) <= 1:
        return []
    texts = [c["text"] for c in chunks]
    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                                 max_features=5000).fit_transform(texts)
        sims = cosine_similarity(matrix[:-1], matrix[1:]).diagonal()
    except ValueError:
        return []
    # A lower sensitivity value means more boundaries.
    threshold = max(0.05, min(0.95, sensitivity))
    return [i + 1 for i, sim in enumerate(sims) if sim < threshold]


def _sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.split()) >= 4]


def summarize_text(text, max_sentences=3):
    """Simple extractive summarizer; ranks sentences by word frequency."""
    sentences = _sentences(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences) if sentences else text[:500]
    words = re.findall(r"\b[a-zA-Z][a-zA-Z']+\b", text.lower())
    freq = Counter(w for w in words if w not in STOPWORDS and len(w) > 2)
    if not freq:
        return " ".join(sentences[:max_sentences])
    max_freq = max(freq.values())
    scores = {}
    for idx, sentence in enumerate(sentences):
        tokens = re.findall(r"\b[a-zA-Z][a-zA-Z']+\b", sentence.lower())
        scores[idx] = sum(freq[t] / max_freq for t in tokens if t in freq) / max(1, len(tokens)) ** 0.5
    selected = sorted(sorted(scores, key=scores.get, reverse=True)[:max_sentences])
    return " ".join(sentences[i] for i in selected)


def _make_title(text):
    words = re.findall(r"\b[a-zA-Z][a-zA-Z']+\b", text.lower())
    counts = Counter(w for w in words if w not in STOPWORDS and len(w) > 2)
    top = [w for w, _ in counts.most_common(4)]
    return " ".join(w.capitalize() for w in top) or "Video discussion"


def build_chapters(transcript, chunk_seconds=75, sensitivity=0.45, max_summary_sentences=3):
    chunks = make_time_chunks(transcript, chunk_seconds)
    if not chunks:
        return []
    boundaries = [0] + _topic_boundaries(chunks, sensitivity) + [len(chunks)]
    chapters = []
    for left, right in zip(boundaries[:-1], boundaries[1:]):
        group = chunks[left:right]
        text = " ".join(c["text"] for c in group).strip()
        if not text:
            continue
        chapters.append({
            "start": group[0]["start"],
            "title": _make_title(text),
            "summary": summarize_text(text, max_sentences=max_summary_sentences),
            "text": text
        })
    return chapters
