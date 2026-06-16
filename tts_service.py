import edge_tts
import uuid
import os
import asyncio
import hashlib
import json

AUDIO_DIR = "audio_cache"
CACHE_FILE = os.path.join(AUDIO_DIR, "cache.json")
os.makedirs(AUDIO_DIR, exist_ok=True)


def load_cache():
    """Load text->filename cache from JSON file"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_cache(cache_data):
    """Save text->filename cache to JSON file"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        print(f"⚠️ Lỗi lưu cache: {e}")


def get_cache_key(text, voice, rate, pitch):
    """Generate cache key từ text + voice + settings"""
    combined = f"{text}|{voice}|{rate}|{pitch}"
    return hashlib.md5(combined.encode()).hexdigest()

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
    """Generate audio using Edge TTS with caching"""
    preset = VOICE_PRESETS.get(voice, {})
    base_voice = preset.get("base_voice", voice)
    rate = rate or preset.get("rate_override", "+0%")
    pitch = pitch or preset.get("pitch_override", "+0Hz")

    # Check cache
    cache_key = get_cache_key(text, voice, rate, pitch)
    cache_data = load_cache()

    if cache_key in cache_data:
        cached_file = cache_data[cache_key]
        cached_path = os.path.join(AUDIO_DIR, cached_file)
        if os.path.exists(cached_path):
            print(f"✅ Cache hit: {cached_file}")
            return cached_path
        else:
            # File was deleted, remove stale cache entry
            del cache_data[cache_key]
            save_cache(cache_data)
            print(f"⚠️ Stale cache entry removed: {cached_file}")

    # Generate new audio
    file_name = f"{cache_key}.mp3"
    file_path = os.path.join(AUDIO_DIR, file_name)

    communicate = edge_tts.Communicate(
        text=text,
        voice=base_voice,
        rate=rate,
        pitch=pitch
    )

    await communicate.save(file_path)

    # Save to cache
    cache_data[cache_key] = file_name
    save_cache(cache_data)
    print(f"📝 Cached: {file_name}")

    return file_path
