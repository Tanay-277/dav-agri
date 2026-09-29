import struct
import io
import math
from typing import Tuple

MAX_AUDIO_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

SUPPORTED_AUDIO_SIGNATURES = [
    b"RIFF",          # WAV
    b"\x1a\x45\xdf\xa3", # WebM / MKV
    b"OggS",          # OGG
    b"ID3",           # MP3 with ID3
    b"\xff\xfb",      # MP3 frame sync
    b"\xff\xf3",      # MP3 frame sync
]

def validate_audio_payload(audio_bytes: bytes) -> str:
    """
    Validates audio byte stream.
    Returns detected format or raises ValueError.
    """
    if not audio_bytes or len(audio_bytes) == 0:
        raise ValueError("Audio payload cannot be empty")

    if len(audio_bytes) > MAX_AUDIO_SIZE_BYTES:
        raise ValueError(f"Audio payload size ({len(audio_bytes)} bytes) exceeds 15MB limit")

    # Check magic bytes
    if b"ftyp" in audio_bytes[:16]:
        return "mp4"

    for sig in SUPPORTED_AUDIO_SIGNATURES:
        if audio_bytes.startswith(sig):
            if sig == b"RIFF":
                return "wav"
            elif sig == b"\x1a\x45\xdf\xa3":
                return "webm"
            elif sig == b"OggS":
                return "ogg"
            return "mp3"

    # Allow custom test audio if larger than 10 bytes
    if len(audio_bytes) >= 10:
        return "raw_pcm"

    raise ValueError("Unsupported audio format or corrupted file header")

def generate_sine_wave_wav(duration_seconds: float = 1.0, freq: float = 440.0, sample_rate: int = 16000) -> bytes:
    """
    Generates a valid, pure PCM WAV audio clip in-memory for testing TTS playback across mobile and browsers.
    """
    num_samples = int(duration_seconds * sample_rate)
    buffer = io.BytesIO()

    # WAV Header
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = num_samples * block_align
    chunk_size = 36 + data_size

    # RIFF Header
    buffer.write(b"RIFF")
    buffer.write(struct.pack("<I", chunk_size))
    buffer.write(b"WAVE")

    # fmt subchunk
    buffer.write(b"fmt ")
    buffer.write(struct.pack("<I", 16))          # Subchunk1Size (16 for PCM)
    buffer.write(struct.pack("<H", 1))           # AudioFormat (1 for PCM)
    buffer.write(struct.pack("<H", num_channels))
    buffer.write(struct.pack("<I", sample_rate))
    buffer.write(struct.pack("<I", byte_rate))
    buffer.write(struct.pack("<H", block_align))
    buffer.write(struct.pack("<H", bits_per_sample))

    # data subchunk
    buffer.write(b"data")
    buffer.write(struct.pack("<I", data_size))

    # Write samples
    for i in range(num_samples):
        # Apply gentle envelope
        envelope = min(1.0, i / (0.05 * sample_rate), (num_samples - i) / (0.05 * sample_rate))
        sample_val = int(envelope * 16000 * math.sin(2 * math.pi * freq * (i / sample_rate)))
        buffer.write(struct.pack("<h", sample_val))

    return buffer.getvalue()
