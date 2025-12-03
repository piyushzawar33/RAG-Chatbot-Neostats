from pathlib import Path

DATA_DIR = Path("data")
CLEANED_TRANSCRIPT_PATH = DATA_DIR / "cleaned_transcript.txt"


def load_cleaned_transcript() -> str:
    if not CLEANED_TRANSCRIPT_PATH.exists():
        raise FileNotFoundError(
            f"Transcript file not found at {CLEANED_TRANSCRIPT_PATH}. "
            "Please create it by copying the YouTube transcript into this file."
        )

    with CLEANED_TRANSCRIPT_PATH.open("r", encoding="utf-8") as f:
        text = f.read()

    return text