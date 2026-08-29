from __future__ import annotations

import json
from pathlib import Path

from text_to_speech.languages import SUPPORTED_LANGUAGES

_DATASET_PATH = Path(__file__).parent / "test_dataset.json"

SPEECH_TEST_DATASET: dict[str, dict[str, list[str]]] = {}
if _DATASET_PATH.exists():
    with open(_DATASET_PATH, "r", encoding="utf-8") as _f:
        SPEECH_TEST_DATASET = json.load(_f)

if not SPEECH_TEST_DATASET:
    SPEECH_TEST_DATASET = {
        "en": {"phrases": ["rain", "temperature", "yield", "soil moisture", "55 millimeters", "30 degrees"]},
        "hi": {"phrases": ["barish", "temperature", "utpatti", "mitti", "55 millimeters"]},
    }


def get_test_phrases(language: str = "en") -> list[str]:
    lang = SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES["en"]).code
    return SPEECH_TEST_DATASET.get(lang, {}).get("phrases", [])


def get_all_test_phrases() -> dict[str, list[str]]:
    result = {}
    for code in SUPPORTED_LANGUAGES:
        result[code] = get_test_phrases(code)
    return result
