import logging
import time
from typing import Dict, Any, Optional, List

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://rest.isric.org/soilgrids/v2.0"

# SoilGrids property codes -> our friendly output keys
PROPERTY_MAP = {
    "phh2o": "ph",
    "soc": "organic_carbon_g_kg",
    "bdod": "bulk_density_kg_m3",
    "cec": "cec_mmolc_kg",
    "nitrogen": "nitrogen_g_kg",
    "sand": "sand_pct",
    "silt": "silt_pct",
    "clay": "clay_pct",
    "caco3": "calcium_carbonate_pct",
    "ocs": "organic_carbon_stock_t_ha",
    "ocst": "organic_carbon_stock_topsoil_t_ha",
    "wwp": "wilting_point_pct",
    "cfvo": "coarse_fragments_pct",
}

# Standard depths requested by the caller
STANDARD_DEPTHS = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]

# Cache TTL in seconds (24 hours)
CACHE_TTL_SECONDS = 24 * 60 * 60


class SoilGridsProvider:
    """Fetches soil property data from ISRIC SoilGrids REST API v2.0."""

    def __init__(self, base_url: str = BASE_URL, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._cache: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_soil_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Return structured soil data for a location, using a 24h cache."""
        cache_key = f"{lat:.4f},{lon:.4f}"
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached["_fetched_at"]) < CACHE_TTL_SECONDS:
            return cached["data"]

        layers = list(PROPERTY_MAP.keys())
        depths = STANDARD_DEPTHS
        url = self._build_query_url(lat, lon, layers, depths)

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url)
                if res.status_code != 200:
                    logger.warning("SoilGrids query failed: HTTP %s", res.status_code)
                    raise RuntimeError(f"SoilGrids returned status {res.status_code}")
                payload = res.json()
        except Exception as e:
            logger.warning("SoilGrids request error: %s", e)
            raise

        data = self._parse_response(lat, lon, payload)
        self._cache[cache_key] = {"_fetched_at": time.time(), "data": data}
        return data

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_query_url(
        self,
        lat: float,
        lon: float,
        layers: List[str],
        depths: List[str],
    ) -> str:
        params = [
            f"lon={lon}",
            f"lat={lat}",
            f"layers={','.join(layers)}",
            f"depths={','.join(depths)}",
            "values=mean",
        ]
        return f"{self.base_url}/properties/query?" + "&".join(params)

    def _parse_response(
        self,
        lat: float,
        lon: float,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        properties: Dict[str, Dict[str, float]] = {}

        # SoilGrids returns:
        # {"properties": {"phh2o": {"depths": {"0-5cm": {"mean": 6.5}, ...}}, ...}}
        for code, friendly in PROPERTY_MAP.items():
            properties[friendly] = {}
            layer_data = payload.get("properties", {}).get(code, {})
            for depth in STANDARD_DEPTHS:
                depth_data = layer_data.get("depths", {}).get(depth, {})
                mean_value = depth_data.get("mean")
                if mean_value is not None:
                    properties[friendly][depth] = mean_value

        return {
            "location": f"{lat},{lon}",
            "properties": properties,
            "source": "soilgrids",
            "is_live": True,
        }


# Module-level singleton for convenience
soilgrids_provider = SoilGridsProvider()

print("SOILGRIDS_CREATED")
