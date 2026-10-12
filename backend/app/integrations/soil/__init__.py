from app.integrations.soil.mock_provider import MockSoilProvider
from app.integrations.soil.soilgrids_provider import SoilGridsProvider

_soil_provider = None
_fallback = MockSoilProvider()

def get_soil_provider() -> SoilGridsProvider:
    global _soil_provider
    if _soil_provider is None:
        _soil_provider = SoilGridsProvider()
    return _soil_provider

def get_soil_provider_safe():
    """Returns the live provider, falling back to mock on failure."""
    try:
        provider = get_soil_provider()
        # quick liveness probe
        provider.get_soil_data(lat=18.5, lon=73.8)
        return provider
    except Exception:
        return _fallback
