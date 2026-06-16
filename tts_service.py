import edge_tts
import uuid
import os
import asyncio

AUDIO_DIR = "audio_cache"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ============================================
# 🇻🇳 PRESET GIỌNG VIỆT (MULTI-PROVIDER)
# ============================================

VOICE_PRESETS = {
    # ======================
    # 🟦 EDGE TTS - Miền Bắc
    # ======================

    "vi-VN-HoaiMyNeural": {
        "name": "👩 Hoài My (Nữ - Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-HoaiMyNeural",
        "region": "north",
        "rate_override": "+0%",
        "pitch_override": "+0Hz"
    },

    "vi-VN-HoaiMyNeural-slow": {
        "name": "👩 Hoài My - Đọc Chậm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-HoaiMyNeural",
        "region": "north",
        "rate_override": "-35%",
        "pitch_override": "+6Hz"
    },

    "vi-VN-HoaiMyNeural-veryslow": {
        "name": "👩 Hoài My - Rất Chậm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-HoaiMyNeural",
        "region": "north",
        "rate_override": "-50%",
        "pitch_override": "+8Hz"
    },

    "vi-VN-HoaiMyNeural-story": {
        "name": "👩 Hoài My - Giọng Mềm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-HoaiMyNeural",
        "region": "north",
        "rate_override": "-10%",
        "pitch_override": "-2Hz"
    },

    "vi-VN-HoaiMyNeural-podcast": {
        "name": "👩 Hoài My - Podcast (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-HoaiMyNeural",
        "region": "north",
        "rate_override": "+20%",
        "pitch_override": "+0Hz"
    },

    "vi-VN-NamMinhNeural": {
        "name": "👨 Nam Minh (Nam - Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "+0%",
        "pitch_override": "+0Hz"
    },

    "vi-VN-NamMinhNeural-slow": {
        "name": "👨 Nam Minh - Đọc Chậm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "-30%",
        "pitch_override": "+3Hz"
    },

    "vi-VN-NamMinhNeural-veryslow": {
        "name": "👨 Nam Minh - Rất Chậm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "-50%",
        "pitch_override": "+5Hz"
    },

    "vi-VN-NamMinhNeural-story": {
        "name": "👨 Nam Minh - Giọng Mềm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "-10%",
        "pitch_override": "-3Hz"
    },

    "vi-VN-NamMinhNeural-deep": {
        "name": "👨 Nam Minh - Giọng Sâu (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "-5%",
        "pitch_override": "-5Hz"
    },

    "vi-VN-NamMinhNeural-podcast": {
        "name": "👨 Nam Minh - Podcast (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "+20%",
        "pitch_override": "+0Hz"
    },
}


async def generate_audio(text: str, voice: str, rate: str = None, pitch: str = None):
    """Generate audio using Edge TTS"""
    file_name = f"{uuid.uuid4()}.mp3"
    file_path = os.path.join(AUDIO_DIR, file_name)

    preset = VOICE_PRESETS.get(voice, {})
    base_voice = preset.get("base_voice", voice)
    rate = rate or preset.get("rate_override", "+0%")
    pitch = pitch or preset.get("pitch_override", "+0Hz")

    communicate = edge_tts.Communicate(
        text=text,
        voice=base_voice,
        rate=rate,
        pitch=pitch
    )

    await communicate.save(file_path)
    return file_path
