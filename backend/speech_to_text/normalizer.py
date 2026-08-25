from __future__ import annotations

import re

from speech_to_text.languages import get_language_config

FILLER_PATTERNS = [
    r"\bplease\b",
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bi want to\b",
    r"\bi would like to\b",
    r"\btell me\b",
    r"\bcan you tell me\b",
    r"\bwould you\b",
    r"\bjust\b",
    r"\bkindly\b",
    r"\bplease tell me\b",
    r"\bi need to know\b",
    r"\bi would like to know\b",
    r"\bcan you please\b",
    r"\bcould you please\b",
    r"\bum+\b",
    r"\buh+\b",
    r"\bhh\b",
    r"\baa\b",
    r"\btheek hai\b",
    r"\bhai na\b",
    r"\bmatlab\b",
    r"\bactually\b",
    r"\bbasically\b",
    r"\bso\b",
    r"\blook\b",
    r"\bbhai\b",
    r"\bdada\b",
    r"\banna\b",
    r"\bthambi\b",
]


class TranscriptNormalizer:
    """Normalizes raw STT output for downstream NLU processing."""

    def __init__(self, language: str = "en") -> None:
        self.language = language
        self._filler_re = re.compile("|".join(FILLER_PATTERNS), re.IGNORECASE)
        self._whitespace_re = re.compile(r"\s+")
        self._punct_re = re.compile(r"[^\w\s]")

    def normalize(self, transcript: str) -> str:
        if not transcript or not transcript.strip():
            return ""
        text = transcript.strip()
        text = self._remove_fillers(text)
        text = self._punct_re.sub("", text)
        text = self._whitespace_re.sub(" ", text).strip()
        text = text.lower()
        return text

    def _remove_fillers(self, text: str) -> str:
        return self._filler_re.sub("", text)

    def set_language(self, language: str) -> None:
        self.language = language


def normalize_transcript(transcript: str, language: str = "en") -> str:
    normalizer = TranscriptNormalizer(language=language)
    return normalizer.normalize(transcript)
