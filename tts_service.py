import edge_tts
import os
import hashlib
import json
import inspect
from typing import Optional, Dict, Any

AUDIO_DIR = "audio_cache"
CACHE_FILE = os.path.join(AUDIO_DIR, "cache.json")

os.makedirs(AUDIO_DIR, exist_ok=True)


def load_cache() -> Dict[str, str]:
    """Load text->filename cache from JSON file"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Lỗi đọc cache: {e}")
            return {}

    return {}


def save_cache(cache_data: Dict[str, str]) -> None:
    """Save text->filename cache to JSON file"""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Lỗi lưu cache: {e}")


def get_cache_key(text: str, voice: str, rate: Optional[str], pitch: Optional[str]) -> str:
    """Generate cache key từ text + voice + settings"""
    combined = f"{text}|{voice}|{rate}|{pitch}"
    return hashlib.md5(combined.encode("utf-8")).hexdigest()


def edge_tts_supports_param(param_name: str) -> bool:
    """
    Kiểm tra edge_tts.Communicate hiện tại có hỗ trợ tham số rate/pitch không.
    Một số version edge-tts cũ không hỗ trợ pitch.
    """
    try:
        signature = inspect.signature(edge_tts.Communicate)
        return param_name in signature.parameters
    except Exception:
        return False


# ============================================
# 🇻🇳 PRESET GIỌNG VIỆT
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
        "pitch_override": "+0Hz",
    },

    "vi-VN-HoaiMyNeural-slow": {
        "name": "👩 Hoài My - Đọc Chậm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-HoaiMyNeural",
        "region": "north",
        "rate_override": "-35%",
        "pitch_override": "+6Hz",
    },

    "vi-VN-HoaiMyNeural-veryslow": {
        "name": "👩 Hoài My - Rất Chậm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-HoaiMyNeural",
        "region": "north",
        "rate_override": "-50%",
        "pitch_override": "+8Hz",
    },

    "vi-VN-HoaiMyNeural-story": {
        "name": "👩 Hoài My - Giọng Mềm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-HoaiMyNeural",
        "region": "north",
        "rate_override": "-10%",
        "pitch_override": "-2Hz",
    },

    "vi-VN-HoaiMyNeural-podcast": {
        "name": "👩 Hoài My - Podcast (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-HoaiMyNeural",
        "region": "north",
        "rate_override": "+20%",
        "pitch_override": "+0Hz",
    },

    "vi-VN-NamMinhNeural": {
        "name": "👨 Nam Minh (Nam - Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "+0%",
        "pitch_override": "+0Hz",
    },

    "vi-VN-NamMinhNeural-slow": {
        "name": "👨 Nam Minh - Đọc Chậm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "-30%",
        "pitch_override": "+3Hz",
    },

    "vi-VN-NamMinhNeural-veryslow": {
        "name": "👨 Nam Minh - Rất Chậm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "-50%",
        "pitch_override": "+5Hz",
    },

    "vi-VN-NamMinhNeural-story": {
        "name": "👨 Nam Minh - Giọng Mềm (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "-10%",
        "pitch_override": "-3Hz",
    },

    "vi-VN-NamMinhNeural-deep": {
        "name": "👨 Nam Minh - Giọng Sâu (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "-5%",
        "pitch_override": "-5Hz",
    },

    "vi-VN-NamMinhNeural-podcast": {
        "name": "👨 Nam Minh - Podcast (Edge TTS)",
        "provider": "edge",
        "language": "Vietnamese",
        "base_voice": "vi-VN-NamMinhNeural",
        "region": "north",
        "rate_override": "+20%",
        "pitch_override": "+0Hz",
    },
}


async def generate_audio(
    text: str,
    voice: str,
    rate: Optional[str] = None,
    pitch: Optional[str] = None,
) -> str:
    """Generate audio using Edge TTS with caching"""

    preset = VOICE_PRESETS.get(voice)

    if not preset:
        raise ValueError(f"Voice '{voice}' not found")

    provider = preset.get("provider", "edge")

    if provider != "edge":
        raise ValueError(f"Provider '{provider}' is not supported yet")

    base_voice = preset.get("base_voice", voice)

    final_rate = rate or preset.get("rate_override") or "+0%"
    final_pitch = pitch or preset.get("pitch_override") or "+0Hz"

    support_rate = edge_tts_supports_param("rate")
    support_pitch = edge_tts_supports_param("pitch")

    # Nếu edge_tts không hỗ trợ pitch thì không đưa pitch thật vào cache key.
    # Tránh tạo nhiều file giống nhau chỉ vì pitch khác nhau.
    effective_pitch = final_pitch if support_pitch else "pitch_unsupported"

    cache_key = get_cache_key(
        text=text,
        voice=voice,
        rate=final_rate,
        pitch=effective_pitch,
    )

    cache_data = load_cache()

    if cache_key in cache_data:
        cached_file = cache_data[cache_key]
        cached_path = os.path.join(AUDIO_DIR, cached_file)

        if os.path.exists(cached_path):
            print(f"✅ Cache hit: {cached_file}")
            return cached_path

        del cache_data[cache_key]
        save_cache(cache_data)
        print(f"⚠️ Stale cache entry removed: {cached_file}")

    file_name = f"{cache_key}.mp3"
    file_path = os.path.join(AUDIO_DIR, file_name)

    communicate_kwargs: Dict[str, Any] = {
        "text": text,
        "voice": base_voice,
    }

    if final_rate and support_rate:
        communicate_kwargs["rate"] = final_rate

    if final_pitch and support_pitch:
        communicate_kwargs["pitch"] = final_pitch
    else:
        print(f"⚠️ edge_tts hiện tại không hỗ trợ pitch, bỏ qua pitch={final_pitch}")

    try:
        communicate = edge_tts.Communicate(**communicate_kwargs)

    except TypeError as e:
        error_text = str(e)

        # Fallback 1: nếu lỗi do pitch thì bỏ pitch
        if "pitch" in error_text and "pitch" in communicate_kwargs:
            print("⚠️ Bỏ pitch do edge_tts không hỗ trợ")
            communicate_kwargs.pop("pitch", None)
            communicate = edge_tts.Communicate(**communicate_kwargs)

        # Fallback 2: nếu lỗi do rate thì bỏ rate
        elif "rate" in error_text and "rate" in communicate_kwargs:
            print("⚠️ Bỏ rate do edge_tts không hỗ trợ")
            communicate_kwargs.pop("rate", None)
            communicate = edge_tts.Communicate(**communicate_kwargs)

        else:
            raise e

    await communicate.save(file_path)

    cache_data[cache_key] = file_name
    save_cache(cache_data)

    print(f"📝 Cached: {file_name}")

    return file_path
