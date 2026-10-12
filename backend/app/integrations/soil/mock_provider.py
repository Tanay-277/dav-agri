from typing import Dict, Any

MOCK_SOIL_DATA = {
    "location": "Pune, Maharashtra",
    "properties": {
        "ph": {"0-5cm": 6.8, "5-15cm": 6.9, "15-30cm": 7.0, "30-60cm": 7.1, "60-100cm": 7.2, "100-200cm": 7.2},
        "organic_carbon_g_kg": {"0-5cm": 8.2, "5-15cm": 7.5, "15-30cm": 6.9, "30-60cm": 6.2, "60-100cm": 5.8, "100-200cm": 5.5},
        "bulk_density_kg_m3": {"0-5cm": 1.32, "5-15cm": 1.38, "15-30cm": 1.42, "30-60cm": 1.45, "60-100cm": 1.47, "100-200cm": 1.48},
        "cec_mmolc_kg": {"0-5cm": 24.0, "5-15cm": 22.0, "15-30cm": 21.0, "30-60cm": 20.0, "60-100cm": 19.0, "100-200cm": 19.0},
        "nitrogen_g_kg": {"0-5cm": 0.28, "5-15cm": 0.25, "15-30cm": 0.22, "30-60cm": 0.19, "60-100cm": 0.17, "100-200cm": 0.16},
        "sand_pct": {"0-5cm": 42.0, "5-15cm": 44.0, "15-30cm": 46.0, "30-60cm": 48.0, "60-100cm": 50.0, "100-200cm": 52.0},
        "silt_pct": {"0-5cm": 32.0, "5-15cm": 31.0, "15-30cm": 30.0, "30-60cm": 29.0, "60-100cm": 28.0, "100-200cm": 27.0},
        "clay_pct": {"0-5cm": 26.0, "5-15cm": 25.0, "15-30cm": 24.0, "30-60cm": 23.0, "60-100cm": 22.0, "100-200cm": 21.0},
        "caco3_pct": {"0-5cm": 3.5, "5-15cm": 3.2, "15-30cm": 3.0, "30-60cm": 2.8, "60-100cm": 2.7, "100-200cm": 2.6},
        "ocs_t_ha": {"0-5cm": 26.5, "5-15cm": 23.5, "15-30cm": 21.5, "30-60cm": 19.0, "60-100cm": 17.5, "100-200cm": 16.5},
        "wwp_pct": {"0-5cm": 12.0, "5-15cm": 13.0, "15-30cm": 14.0, "30-60cm": 15.0, "60-100cm": 15.5, "100-200cm": 16.0},
        "cfvo_pct": {"0-5cm": 2.0, "5-15cm": 2.0, "15-30cm": 2.0, "30-60cm": 2.0, "60-100cm": 2.0, "100-200cm": 2.0},
    },
    "source": "mock",
    "is_live": False,
}


class MockSoilProvider:
    """Fallback soil provider returning representative Maharashtra data."""

    def get_soil_data(self, lat: float = None, lon: float = None) -> Dict[str, Any]:
        data = dict(MOCK_SOIL_DATA)
        if lat is not None and lon is not None:
            data["location"] = f"{lat},{lon}"
        return data
