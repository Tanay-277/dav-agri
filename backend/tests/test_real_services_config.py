import pytest
from app.core.config import settings, log_startup_configuration
from app.ai import get_ai_provider, MockAIProvider, GeminiAIProvider
from app.otp import get_otp_provider, MockOTPProvider, ProductionOTPProvider
from app.services.google_auth_service import GoogleAuthService
from app.integrations.weather.mock_provider import MockWeatherProvider
from app.integrations.weather.openmeteo_provider import OpenMeteoWeatherProvider
from app.schemas.weather import AgriculturalWeatherResponse
from app.schemas.query import QueryResponse
from datetime import datetime, timezone

def test_ai_provider_resolution():
    # In dev without GEMINI_API_KEY, returns MockAIProvider
    provider = get_ai_provider()
    assert isinstance(provider, MockAIProvider)
    assert provider.provider_name == "mock"

    # Explicit Gemini provider instantiation
    gemini_prov = GeminiAIProvider(api_key="test_fake_api_key_123")
    assert gemini_prov.provider_name == "gemini"
    assert gemini_prov.api_key == "test_fake_api_key_123"

def test_ai_language_lock_and_validation():
    provider = MockAIProvider()
    facts = {"intent": "production_trend", "total_growth_quintals": 9.0, "percentage_increase": 75.0, "first_year": 2022, "last_year": 2025}
    
    # Supported languages
    resp_mr = provider.generate_explanation("कापूस", facts, language="mr")
    assert "उत्पादन" in resp_mr or "वाढ" in resp_mr
    
    resp_hi = provider.generate_explanation("कपास", facts, language="hi")
    assert "उत्पादन" in resp_hi or "वृद्धि" in resp_hi
    
    resp_en = provider.generate_explanation("cotton", facts, language="en")
    assert "production" in resp_en or "growth" in resp_en

    # Unsupported language must raise ValueError
    with pytest.raises(ValueError, match="Unsupported language code"):
        provider.generate_explanation("cotton", facts, language="es")

def test_gemini_fallback_on_network_error(monkeypatch):
    """When Gemini API call encounters network error, it must fall back cleanly without crashing."""
    gemini = GeminiAIProvider(api_key="invalid_test_key_xyz")
    facts = {"intent": "production_trend", "total_growth_quintals": 9.0, "percentage_increase": 75.0, "first_year": 2022, "last_year": 2025}
    
    # generate_explanation should not crash; it logs error and returns fallback
    explanation = gemini.generate_explanation("Tell me about cotton", facts, language="en")
    assert isinstance(explanation, str)
    assert len(explanation) > 0
    assert "production" in explanation.lower()

    # classify_intent should also fall back safely
    intent = gemini.classify_intent("कापूस उत्पादन कसे वाढले?")
    assert intent == "production_trend"

def test_otp_provider_mock_and_production():
    # Dev mode OTP provider
    otp_prov = get_otp_provider()
    assert isinstance(otp_prov, MockOTPProvider)
    assert otp_prov.is_production is False
    assert otp_prov.provider_name == "mock"
    assert otp_prov.generate_otp() == "44444"
    assert otp_prov.send_otp("9876543210", "44444") is True

    # Production Twilio OTP provider
    prod_otp = ProductionOTPProvider(
        account_sid="ACtest1234567890",
        auth_token="authtokentest123",
        from_number="+15005550006"
    )
    assert prod_otp.is_production is True
    assert prod_otp.provider_name == "twilio"
    otp_code = prod_otp.generate_otp()
    assert len(otp_code) == 5
    assert otp_code.isdigit()

def test_twilio_otp_missing_credentials_rejection():
    broken_prod_otp = ProductionOTPProvider(account_sid="", auth_token="", from_number="")
    with pytest.raises(RuntimeError, match="Twilio SMS credentials are not properly configured"):
        broken_prod_otp.send_otp("9876543210", "12345")

def test_google_auth_service():
    # In dev without GOOGLE_CLIENT_ID, returns simulated user profile
    res = GoogleAuthService.verify_id_token("sample_test_id_token")
    assert "google_id" in res
    assert res["google_id"].startswith("g_")
    assert res["email"] == "farmer@dav.local"

    # Empty token rejected
    with pytest.raises(ValueError, match="Google ID token cannot be empty"):
        GoogleAuthService.verify_id_token("")

def test_weather_metadata_and_providers():
    mock_weather = MockWeatherProvider()
    resp = mock_weather.get_agricultural_weather(18.52, 73.85, "Pune, MH")
    assert isinstance(resp, AgriculturalWeatherResponse)
    assert resp.is_live is False
    assert resp.source == "mock"

    # OpenMeteo provider has is_live and source
    openmeteo = OpenMeteoWeatherProvider()
    live_resp = openmeteo.get_agricultural_weather(18.52, 73.85, "Pune, MH")
    assert isinstance(live_resp, AgriculturalWeatherResponse)
    assert live_resp.source in ("openmeteo", "mock")

def test_query_response_source_field():
    q_resp = QueryResponse(
        id="q_123",
        query="Test query",
        language="en",
        intent="production_trend",
        answer="Production increased by 75%.",
        source="gemini",
        created_at=datetime.now(timezone.utc)
    )
    assert q_resp.source == "gemini"

def test_startup_diagnostics_and_production_guard(monkeypatch):
    # In development mode, runs without throwing
    log_startup_configuration()

    # In production mode with default dev secret, must raise RuntimeError
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    with pytest.raises(RuntimeError, match="CRITICAL SECURITY ERROR"):
        log_startup_configuration()

def test_backend_root_endpoint_html_status_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "DAV" in body
    assert "Digital Agricultural Voice" in body
    assert "ONLINE" in body
    assert "/docs" in body
    assert "/health" in body

def test_backend_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "dav-backend"
    assert data["version"] == "1.0.0"

