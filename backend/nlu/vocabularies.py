from __future__ import annotations

STATES: tuple[str, ...] = (
    "Andhra Pradesh",
    "Gujarat",
    "Karnataka",
    "Madhya Pradesh",
    "Maharashtra",
    "Punjab",
    "Rajasthan",
    "Tamil Nadu",
)

DISTRICTS: dict[str, tuple[str, ...]] = {
    "Andhra Pradesh": ("Guntur", "Kurnool", "Tirupati", "Vijayawada", "Visakhapatnam"),
    "Gujarat": ("Ahmedabad", "Bhavnagar", "Rajkot", "Surat", "Vadodara"),
    "Karnataka": ("Bangalore", "Belgaum", "Gulbarga", "Mysore", "Shimoga"),
    "Madhya Pradesh": ("Bhopal", "Gwalior", "Indore", "Jabalpur", "Ujjain"),
    "Maharashtra": ("Aurangabad", "Kolhapur", "Nagpur", "Nashik", "Pune"),
    "Punjab": ("Amritsar", "Bathinda", "Jalandhar", "Ludhiana", "Patiala"),
    "Rajasthan": ("Ajmer", "Jaipur", "Jodhpur", "Kota", "Udaipur"),
    "Tamil Nadu": ("Coimbatore", "Madras", "Madurai", "Salem", "Tiruchirappalli"),
}

CROPS: tuple[str, ...] = (
    "Cotton",
    "Groundnut",
    "Maize",
    "Pulses",
    "Rice",
    "Soybean",
    "Sugarcane",
    "Wheat",
)

METRIC_ALIASES: dict[str, str] = {
    "rain": "rainfall_mm",
    "rainfall": "rainfall_mm",
    "rain water": "rainfall_mm",
    "precipitation": "rainfall_mm",
    "temperature": "temperature_c",
    "temp": "temperature_c",
    "heat": "temperature_c",
    "hot": "temperature_c",
    "cold": "temperature_c",
    "humidity": "humidity_pct",
    "moisture": "soil_moisture_pct",
    "soil moisture": "soil_moisture_pct",
    "yield": "yield_kg_per_ha",
    "production": "production_tonnes",
    "crop": "yield_kg_per_ha",
    "wind": "wind_speed_kmh",
    "speed": "wind_speed_kmh",
    "forecast": "precipitation_probability_pct",
    "weather": "rainfall_mm",
}

METRIC_DISPLAY_NAMES: dict[str, str] = {
    "rainfall_mm": "Rainfall",
    "temperature_c": "Temperature",
    "humidity_pct": "Humidity",
    "soil_moisture_pct": "Soil Moisture",
    "yield_kg_per_ha": "Yield",
    "production_tonnes": "Production",
    "wind_speed_kmh": "Wind Speed",
    "precipitation_probability_pct": "Rain Probability",
}

THRESHOLDS: dict[str, dict[str, float]] = {
    "rainfall_mm": {"low": 50.0, "high": 300.0},
    "temperature_c": {"low": 10.0, "high": 40.0},
    "humidity_pct": {"low": 30.0, "high": 90.0},
    "soil_moisture_pct": {"low": 20.0, "high": 80.0},
    "wind_speed_kmh": {"low": 0.0, "high": 50.0},
}

INTENT_TRIGGERS: dict[str, list[str]] = {
    "help": ["help", "what can you do", "commands", "options", "how to use"],
    "reset": ["reset", "clear", "remove filters", "show all"],
    "read_aloud": ["read aloud", "tell me the story", "narrate", "speak"],
    "stop": ["stop", "cancel", "shut up", "quiet"],
    "pause": ["pause", "wait", "hold on"],
    "resume": ["resume", "continue", "go on"],
    "recommendation_query": [
        "what should i do", "what should we do", "recommend", "suggestion",
        "advice", "should i irrigate", "should we irrigate", "action",
        "recommendation", "what actions should i take",
    ],
    "anomaly_query": [
        "anomaly", "anomalous", "unusual", "outlier", "odd", "strange",
        "abnormal", "different", "weird",
    ],
    "trend_query": [
        "trend", "increasing", "decreasing", "going up", "going down",
        "rising", "falling", "pattern", "over time",
    ],
    "forecast": [
        "forecast", "tomorrow", "next day", "future", "predict", "will it",
        "going to", "expected", "next week", "next month", "kal",
    ],
    "historical_query": [
        "yesterday", "last week", "last month", "previous", "past",
        "histor", "history", "historical", "was the weather", "what was",
    ],
    "comparison": [
        "compare", "comparison", "vs", "versus", "difference", "better",
        "worse", "hotter", "colder", "more rain", "less rain", "higher",
        "lower", "than",
    ],
    "threshold_query": [
        "low", "high", "below", "above", "threshold", "too hot", "too cold",
        "too dry", "too wet", "is it dry", "is it wet",
    ],
    "wind_query": ["wind", "windy", "strong wind", "gust"],
    "humidity_query": ["humidity", "humid", "dry"],
    "soil_query": ["soil moisture", "soil", "ground moisture"],
    "rainfall_query": ["rain", "rainfall", "raining", "precipitation", "how much rain", "will it rain"],
    "temperature_query": ["temperature", "temp", "how hot", "how cold", "degree"],
    "yield_query": ["yield", "production", "harvest", "output"],
    "current_conditions": [
        "current", "now", "today", "present", "right now", "at the moment",
        "weather like", "conditions", "mausam ka haal", "mausam kya hai",
    ],
    "filter": [
        "show", "filter", "data for", "all crops", "all states",
        "display", "get", "find",
    ],
}

COMPARISON_PHRASES: list[str] = [
    "compare", "comparison", "vs", "versus", "difference", "better", "worse",
]

HISTORICAL_QUERY: list[str] = [
    "yesterday", "last week", "last month", "previous", "past",
    "histor", "was the weather", "what was",
]

RELATIVE_DATE_PATTERNS: dict[str, str] = {
    r"\btoday\b": "today",
    r"\btomorrow\b": "tomorrow",
    r"\byesterday\b": "yesterday",
    r"\bnext week\b": "next_week",
    r"\blast week\b": "last_week",
    r"\bnext month\b": "next_month",
    r"\blast month\b": "last_month",
}

UNSUPPORTED_INDICATORS: list[str] = [
    "stock", "price", "market", "buy", "sell", "cost",
    "email", "send", "call", "phone", "sms", "message",
    "login", "password", "account", "register", "sign up",
    "fertilizer recommendation", "pesticide", "seed variety",
    "government scheme", "loan", "insurance",
]

LANGUAGE_KEYWORDS: dict[str, list[str]] = {
    "hi": ["mausam", "kya", "hai", "kal", "barish", "hogi", "mein", "temperature", "gehun", "liye", "karana", "chahiye", "kitna"],
    "ta": ["velli", "nilam"],
    "te": ["velli", "nilam"],
    "kn": ["velli", "nilam"],
    "bn": ["velli", "nilam"],
}
