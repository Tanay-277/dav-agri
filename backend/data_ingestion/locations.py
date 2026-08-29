from __future__ import annotations

# Controlled vocabulary for states and districts based on the MVRS dataset.
NORMALIZED_STATES: tuple[str, ...] = (
    "Andhra Pradesh",
    "Gujarat",
    "Karnataka",
    "Madhya Pradesh",
    "Maharashtra",
    "Punjab",
    "Rajasthan",
    "Tamil Nadu",
)

NORMALIZED_DISTRICTS: dict[str, tuple[str, ...]] = {
    "Andhra Pradesh": ("Guntur", "Kurnool", "Tirupati", "Vijayawada", "Visakhapatnam"),
    "Gujarat": ("Ahmedabad", "Bhavnagar", "Rajkot", "Surat", "Vadodara"),
    "Karnataka": ("Bangalore", "Belgaum", "Gulbarga", "Mysore", "Shimoga"),
    "Madhya Pradesh": ("Bhopal", "Gwalior", "Indore", "Jabalpur", "Ujjain"),
    "Maharashtra": ("Aurangabad", "Kolhapur", "Nagpur", "Nashik", "Pune"),
    "Punjab": ("Amritsar", "Bathinda", "Jalandhar", "Ludhiana", "Patiala"),
    "Rajasthan": ("Ajmer", "Jaipur", "Jodhpur", "Kota", "Udaipur"),
    "Tamil Nadu": ("Coimbatore", "Madras", "Madurai", "Salem", "Tiruchirappalli"),
}

LOCATION_CENTROIDS: dict[str, tuple[float, float]] = {
    "andhra_pradesh_guntur": (16.3067, 80.4365),
    "andhra_pradesh_kurnool": (15.8281, 78.0373),
    "andhra_pradesh_tirupati": (13.6288, 79.4192),
    "andhra_pradesh_vijayawada": (16.5062, 80.6480),
    "andhra_pradesh_visakhapatnam": (17.6868, 83.2185),
    "gujarat_ahmedabad": (23.0225, 72.5714),
    "gujarat_bhavnagar": (21.7645, 72.1519),
    "gujarat_rajkot": (22.3039, 70.8022),
    "gujarat_surat": (21.1702, 72.8311),
    "gujarat_vadodara": (22.3072, 73.1812),
    "karnataka_bangalore": (12.9716, 77.5946),
    "karnataka_belgaum": (15.8497, 74.4977),
    "karnataka_gulbarga": (17.3297, 76.8343),
    "karnataka_mysore": (12.2958, 76.6399),
    "karnataka_shimoga": (13.9299, 75.5681),
    "madhya_pradesh_bhopal": (23.2599, 77.4126),
    "madhya_pradesh_gwalior": (26.2183, 78.1828),
    "madhya_pradesh_indore": (22.7196, 75.8577),
    "madhya_pradesh_jabalpur": (23.1815, 79.9864),
    "madhya_pradesh_ujjain": (23.1793, 75.7849),
    "maharashtra_aurangabad": (19.8762, 75.3433),
    "maharashtra_kolhapur": (16.7050, 74.2433),
    "maharashtra_nagpur": (21.1458, 79.0882),
    "maharashtra_nashik": (19.9975, 73.7898),
    "maharashtra_pune": (18.5204, 73.8567),
    "punjab_amritsar": (31.6340, 74.8723),
    "punjab_bathinda": (30.2110, 74.9455),
    "punjab_jalandhar": (31.3260, 75.5762),
    "punjab_ludhiana": (30.9010, 75.8573),
    "punjab_patiala": (30.3398, 76.3869),
    "rajasthan_ajmer": (26.4499, 74.6399),
    "rajasthan_jaipur": (26.9124, 75.7873),
    "rajasthan_jodhpur": (26.2389, 73.0243),
    "rajasthan_kota": (25.2138, 75.8648),
    "rajasthan_udaipur": (24.5854, 73.7125),
    "tamil_nadu_coimbatore": (11.0168, 76.9558),
    "tamil_nadu_madras": (13.0827, 80.2707),
    "tamil_nadu_madurai": (9.9252, 78.1198),
    "tamil_nadu_salem": (11.6643, 78.1460),
    "tamil_nadu_tiruchirappalli": (10.7905, 78.7047),
}


def normalize_state(raw: str | None) -> str | None:
    if raw is None:
        return None
    cleaned = str(raw).strip()
    for state in NORMALIZED_STATES:
        if cleaned.lower() == state.lower():
            return state
    return cleaned.title()


def normalize_district(raw: str | None, state: str | None) -> str | None:
    if raw is None:
        return None
    cleaned = str(raw).strip()
    if state and state in NORMALIZED_DISTRICTS:
        for district in NORMALIZED_DISTRICTS[state]:
            if cleaned.lower() == district.lower():
                return district
    return cleaned.title()


def build_location_id(state: str | None, district: str | None) -> str:
    s = (state or "unknown").strip().lower().replace(" ", "_")
    d = (district or "unknown").strip().lower().replace(" ", "_")
    return f"{s}_{d}"


def get_centroid(location_id: str) -> tuple[float, float] | None:
    return LOCATION_CENTROIDS.get(location_id)
