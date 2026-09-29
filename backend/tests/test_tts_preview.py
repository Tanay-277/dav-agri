from app.services.voice_service import VoiceService, SAMPLE_PHRASES

def test_tts_samples_produce_real_speech(client):
    service = VoiceService()

    # 1. English
    res_en = client.get("/api/v1/voice/sample?language=en")
    assert res_en.status_code == 200
    data_en = res_en.json()["data"]
    assert data_en["sample_text"] == "Hello, I am your voice assistant."
    assert len(data_en["audio_base64"]) > 5000

    # 2. Hindi
    res_hi = client.get("/api/v1/voice/sample?language=hi")
    assert res_hi.status_code == 200
    data_hi = res_hi.json()["data"]
    assert data_hi["sample_text"] == "नमस्ते, मैं आपका वॉइस असिस्टेंट हूँ।"
    assert len(data_hi["audio_base64"]) > 5000

    # 3. Marathi
    res_mr = client.get("/api/v1/voice/sample?language=mr")
    assert res_mr.status_code == 200
    data_mr = res_mr.json()["data"]
    assert data_mr["sample_text"] == "नमस्कार, मी तुमचा व्हॉइस असिस्टंट आहे।"
    assert len(data_mr["audio_base64"]) > 5000

    # 4. Direct synthesis
    synth_res = client.post("/api/v1/voice/synthesize", json={"text": "Test speech", "language": "en"})
    assert synth_res.status_code == 200
    assert len(synth_res.content) > 1000
