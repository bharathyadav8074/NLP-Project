# AI-Based Automatic YouTube Video Chapter Generation and Summarization Using NLP

A beginner-friendly NLP project that accepts a YouTube URL, retrieves its available captions, detects possible topic changes, creates timestamped chapters, and generates extractive summaries.

## Features

- Accepts common YouTube URL formats.
- Retrieves available captions/transcripts.
- Groups transcript segments into time-based chunks.
- Detects topic changes using TF-IDF vectors and cosine similarity.
- Creates automatic chapter titles using frequent keywords.
- Generates extractive summaries for each chapter and the full video.
- Produces clickable timestamps and downloadable Markdown notes.

## Important limitation

This starter project analyzes **captions/transcripts**, not the video's visual frames or raw audio. Chapter boundaries and titles are heuristic estimates, so review them before publishing. It requires captions to be available and accessible. YouTube may restrict automated transcript access.

## Requirements

- Python 3.10 or 3.11 recommended
- Internet connection
- A YouTube video with accessible captions

## Setup (Windows)

```bash
py -3.11 -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Setup (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local Streamlit address shown in the terminal (usually http://localhost:8501).

## How to use

1. Run the app.
2. Paste a public YouTube video URL.
3. Enter the transcript language code (for example `en`, `hi`, or `te`).
4. Choose chunk size and topic-change sensitivity.
5. Click **Generate chapters**.
6. Review the timestamps and summaries.
7. Download the generated Markdown notes.

## Project structure

```text
youtube_chapter_generator/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── src/
    ├── __init__.py
    ├── youtube_transcript.py
    └── pipeline.py
```

## How the NLP pipeline works

1. **Transcript retrieval:** obtains caption segments with start times.
2. **Time chunking:** groups adjacent caption segments into chunks.
3. **Text representation:** TF-IDF converts each chunk into a numerical vector.
4. **Topic segmentation:** cosine similarity compares neighboring chunks. A low similarity can indicate a topic shift.
5. **Chapter title generation:** frequent non-stopword terms become a simple title.
6. **Summarization:** an extractive frequency-based method selects representative sentences.
7. **Timestamp linking:** the first transcript time in each chapter becomes its YouTube timestamp.

## Suggested improvements (good for a college project)

- Replace TF-IDF segmentation with Sentence-BERT embeddings.
- Use a change-point detection algorithm and compare results.
- Replace extractive summaries with a fine-tuned or pretrained BART/T5 summarizer.
- Generate better chapter titles with a text-to-text model.
- Add transcript upload support (`.txt` or `.srt`) when YouTube captions cannot be fetched.
- Add multilingual preprocessing and language detection.
- Evaluate chapter boundaries against manually annotated timestamps using Precision, Recall, and F1.
- Evaluate summaries using ROUGE.
- Add user accounts and save previous analyses in SQLite.

## Troubleshooting

- **No transcript:** choose a video with captions and check the language code.
- **Transcript fetch blocked:** try again later or use a transcript file upload feature you add yourself.
- **Too many chapters:** increase topic-change sensitivity or increase chunk size.
- **Too few chapters:** decrease sensitivity or reduce chunk size.
- **Weak titles:** the baseline title generator is keyword-based; improve it with keyphrase extraction or a transformer model.

## Responsible use

Respect YouTube's terms, copyright, privacy, and applicable API policies. Do not republish full copyrighted transcripts without permission. Use this tool for personal study and analysis.
