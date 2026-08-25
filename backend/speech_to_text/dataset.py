from __future__ import annotations

from speech_to_text.languages import SUPPORTED_LANGUAGES

SPEECH_TEST_DATASET: dict[str, dict[str, list[str]]] = {
    "en": {
        "queries": [
            "What is the weather in Punjab",
            "Will it rain tomorrow",
            "How hot is it today",
            "What is the temperature",
            "Show wheat in Punjab",
            "Is rainfall increasing",
            "Compare tomorrow with today",
            "How is wheat doing",
            "Soil moisture status",
            "Wind speed in Tamil Nadu",
            "Tell me about rain",
            "What should I do",
            "Any unusual weather patterns",
            "Yield data for Maharashtra",
            "Filter by Coimbatore",
            "Help me",
            "Reset filters",
            "Humidity level too high",
            "Temperature trend over the last month",
            "Is there an outlier in temperature data",
        ],
    },
    "hi": {
        "queries": [
            "Mausam ka haal kya hai",
            "Kya kal barish hogi",
            "Punjab mein temperature kya hai",
            "Gehun ke liye kya karana chahiye",
            "Madhya Pradesh mein rainfall kitna hai",
            "Kya rainfall badh rahi hai",
            "Kal aaj se thanda hoga",
            "Gahun ka output kya hai",
            "Mitti mein paani ki matra",
            "Hawa ki tezi kya hai",
        ],
    },
    "ta": {
        "queries": [
            "Velli ennatha",
            "Naalai mazhai peirum",
            "Tamil nadu la temperature enna",
            "Nellai la vegkai padithukoodiya kadhai",
            "Tamil nadu la mazhai ennatha",
            "Temperature athigama irukka",
            "Nalai innum vechu hottu irukka",
            "Punjab la wheat elachu enna",
        ],
    },
    "te": {
        "queries": [
            "Velli ela undi",
            "Roju bavagadi vastundha",
            "Andhra Pradesh lo temperature emiti",
            "Guruvu ela undi",
            "Telangana lo rainfall enni undi",
            "Temperature perigindi",
            "Naalai roju compare chey",
        ],
    },
    "kn": {
        "queries": [
            "Velli hege ide",
            "Naali bartha ideya",
            "Karnataka dalli temperature yestu",
            "Goroo hogayta ideya",
            "Male enu hechide",
            "Temperature erchaagide",
        ],
    },
    "mr": {
        "queries": [
            "Hava kasa ahe",
            "Udya varsha hone ya",
            "Maharashtra madhye tapman kiti ahe",
            "Gandhala kiti ahe",
            "Paus kiti ahe",
            "Aaj thandak ahe ka",
        ],
    },
    "bn": {
        "queries": [
            "Aajkal er bhalo ache",
            "Kallay bosortey para",
            "Banglar tap koto",
            "Gom er fal koto",
            "Barish koyta hocche",
            "Tap berhoiteche",
        ],
    },
}

CATEGORIES = {
    "weather": ["What is the weather in Punjab", "Velli ennatha", "Hava kasa ahe", "Aajkal er bhalo ache"],
    "rain": ["Will it rain tomorrow", "Kya kal barish hogi", "Naalai mazhai peirum", "Kallay bosortey para"],
    "temperature": ["How hot is it today", "Punjab mein temperature kya hai", "Tamil nadu la temperature enna", "Banglar tap koto"],
    "forecast": ["Will it rain tomorrow", "Naalai mavagadi vastundha", "Udya varsha hone ya"],
    "comparisons": ["Compare tomorrow with today", "Kal aaj se thanda hoga", "Naalai innum vechu hottu irukka"],
    "follow_up": ["How is wheat doing", "And temperature", "Yield data for Maharashtra", "Goroo hogayta ideya"],
}

NOISE_LEVELS = ["clean", "low", "medium", "high"]
SPEAKING_SPEEDS = ["slow", "normal", "fast"]
QUERY_LENGTHS = ["short", "medium", "long"]


def get_test_queries(language: str = "en") -> list[str]:
    lang = SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES["en"]).code
    return SPEECH_TEST_DATASET.get(lang, {}).get("queries", [])


def get_category_queries(category: str, language: str = "en") -> list[str]:
    return [q for q in SPEECH_TEST_DATASET.get(language, {}).get("queries", []) if q in CATEGORIES.get(category, [])]
