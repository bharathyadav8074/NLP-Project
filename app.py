import streamlit as st
from src.youtube_transcript import get_video_id, fetch_transcript
from src.pipeline import build_chapters, summarize_text, format_timestamp

st.set_page_config(page_title="YouTube Chapter Generator", page_icon="🎬", layout="wide")
st.title("🎬 AI-Based YouTube Chapter Generation & Summarization")
st.write("Generate topic-based chapters, timestamps, and summaries from a video's transcript.")

with st.sidebar:
    st.header("Settings")
    chunk_seconds = st.slider("Transcript chunk size (seconds)", 30, 180, 75, 15)
    sensitivity = st.slider("Topic-change sensitivity", 0.10, 0.90, 0.45, 0.05,
                            help="Higher values create fewer chapters; lower values create more.")
    max_summary_sentences = st.slider("Summary sentences per chapter", 1, 5, 3)
    st.caption("This starter version uses transcript text. It does not analyze video frames or audio directly.")

url = st.text_input("Paste a YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")
language = st.text_input("Transcript language code", value="en", help="Examples: en, hi, te")

if st.button("Generate chapters", type="primary", disabled=not url.strip()):
    try:
        video_id = get_video_id(url.strip())
        with st.spinner("Fetching transcript..."):
            transcript = fetch_transcript(video_id, language.strip() or "en")
        if not transcript:
            st.error("No transcript was returned for this video.")
            st.stop()

        with st.spinner("Detecting topics and generating summaries..."):
            chapters = build_chapters(transcript, chunk_seconds=chunk_seconds,
                                      sensitivity=sensitivity,
                                      max_summary_sentences=max_summary_sentences)
        if not chapters:
            st.warning("The transcript was too short to create chapters.")
            st.stop()

        st.success(f"Generated {len(chapters)} chapters.")
        st.subheader("Video chapters")
        for i, chapter in enumerate(chapters, start=1):
            start = format_timestamp(chapter["start"])
            st.markdown(f"### {i}. [{start}](https://www.youtube.com/watch?v={video_id}&t={int(chapter['start'])}s) — {chapter['title']}")
            st.write(chapter["summary"])
            with st.expander("View transcript"):
                st.write(chapter["text"])

        st.subheader("Overall summary")
        all_text = " ".join(c["text"] for c in chapters)
        st.write(summarize_text(all_text, max_sentences=8))

        markdown = [f"# YouTube Video Notes\n\nVideo: https://www.youtube.com/watch?v={video_id}\n"]
        for i, c in enumerate(chapters, 1):
            markdown.append(f"## {i}. {format_timestamp(c['start'])} — {c['title']}\n\n{c['summary']}\n")
        st.download_button("Download chapters as Markdown", "\n".join(markdown),
                           file_name=f"{video_id}_chapters.md", mime="text/markdown")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.info("Check that the video has captions and that the transcript language is available.")
else:
    st.info("Enter a public YouTube URL and click **Generate chapters**.")
