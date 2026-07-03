import speech_recognition as sr
import os
import hashlib
import json
from typing import Dict, Optional
import subprocess
import tempfile
from pathlib import Path
import asyncio

import imageio_ffmpeg


TRANSCRIPTION_CACHE_DIR = "transcription_cache"
TRANSCRIPTION_CACHE_FILE = os.path.join(TRANSCRIPTION_CACHE_DIR, "cache.json")

os.makedirs(TRANSCRIPTION_CACHE_DIR, exist_ok=True)

# Supported languages for STT
LANGUAGE_CODES = {
    "vi": "Vietnamese",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "zh": "Chinese",
}

# Language code mapping for Google Speech Recognition
LANGUAGE_CODE_MAP = {
    "vi": "vi-VN",
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "pt": "pt-PT",
    "ru": "ru-RU",
    "ja": "ja-JP",
    "zh": "zh-CN",
}


def load_transcription_cache() -> Dict[str, Dict]:
    """Load audio->transcription cache from JSON file"""
    if os.path.exists(TRANSCRIPTION_CACHE_FILE):
        try:
            with open(TRANSCRIPTION_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Lỗi đọc transcription cache: {e}")
            return {}
    return {}


def save_transcription_cache(cache_data: Dict[str, Dict]) -> None:
    """Save audio->transcription cache to JSON file"""
    try:
        with open(TRANSCRIPTION_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Lỗi lưu transcription cache: {e}")


def get_audio_hash(audio_data: bytes) -> str:
    """Generate hash from audio data for caching"""
    return hashlib.md5(audio_data).hexdigest()


def normalize_audio_format(audio_format: Optional[str]) -> str:
    """
    Convert content-type / extension to a safe file extension.

    Examples:
    - audio/webm -> .webm
    - webm -> .webm
    - audio/ogg;codecs=opus -> .ogg
    - mp3 -> .mp3
    """
    fmt = (audio_format or "").lower().strip()

    if not fmt:
        return ".webm"

    # remove codec part: audio/webm;codecs=opus
    fmt = fmt.split(";")[0].strip()

    # remove audio/
    if fmt.startswith("audio/"):
        fmt = fmt.replace("audio/", "", 1)

    # remove dot
    fmt = fmt.replace(".", "").strip()

    if fmt in ["webm"]:
        return ".webm"

    if fmt in ["ogg", "opus"]:
        return ".ogg"

    if fmt in ["mp3", "mpeg", "mpga"]:
        return ".mp3"

    if fmt in ["mp4", "m4a", "aac", "x-m4a"]:
        return ".m4a"

    if fmt in ["wav", "wave", "x-wav"]:
        return ".wav"

    if fmt in ["flac", "x-flac"]:
        return ".flac"

    # fallback for browser MediaRecorder
    return ".webm"


def convert_audio_to_pcm_wav(audio_data: bytes, audio_format: Optional[str]) -> bytes:
    """
    Convert any uploaded audio to WAV PCM 16-bit mono 16kHz.

    This fixes:
    Audio file could not be read as PCM WAV, AIFF/AIFF-C, or Native FLAC
    """
    input_ext = normalize_audio_format(audio_format)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        input_path = temp_dir_path / f"input{input_ext}"
        output_path = temp_dir_path / "output.wav"

        input_path.write_bytes(audio_data)

        cmd = [
            ffmpeg_exe,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-f",
            "wav",
            str(output_path),
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise Exception(f"FFmpeg convert failed: {result.stderr}")

        if not output_path.exists():
            raise Exception("FFmpeg convert failed: output.wav not found")

        return output_path.read_bytes()


def transcribe_audio_sync(
    audio_data: bytes,
    language: str = "vi",
    audio_format: Optional[str] = "webm",
) -> Dict[str, str]:
    temp_file = None

    try:
        if not audio_data:
            return {
                "status": "error",
                "error": "Audio file is empty",
                "language": language,
            }

        # Check cache first
        cache = load_transcription_cache()
        audio_hash = get_audio_hash(audio_data)
        cache_key = f"{audio_hash}_{language}"

        if cache_key in cache:
            print(f"✅ Cache hit for transcription: {cache_key}")
            return {
                "status": "success",
                "text": cache[cache_key]["text"],
                "language": language,
                "cached": True,
            }

        print(f"🎤 Processing audio file: {audio_format}")

        # Always convert to WAV PCM before SpeechRecognition
        print("🔄 Converting audio to WAV PCM 16kHz mono...")
        wav_data = convert_audio_to_pcm_wav(audio_data, audio_format)

        # Save converted WAV to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_data)
            temp_file = tmp.name

        print("📖 Reading converted WAV file...")

        recognizer = sr.Recognizer()

        with sr.AudioFile(temp_file) as source:
            audio = recognizer.record(source)

        lang_code = LANGUAGE_CODE_MAP.get(language, "vi-VN")

        print(f"🔍 Transcribing audio language={language}, google_lang={lang_code}...")
        text = recognizer.recognize_google(audio, language=lang_code)

        cache[cache_key] = {
            "text": text,
            "language": language,
            "audio_hash": audio_hash,
        }

        save_transcription_cache(cache)

        print(f"✅ Transcription complete: {text[:80]}...")

        return {
            "status": "success",
            "text": text,
            "language": language,
            "cached": False,
        }

    except sr.UnknownValueError:
        return {
            "status": "error",
            "error": "Không nhận diện được giọng nói. File có thể quá nhỏ, quá ồn hoặc không có tiếng nói rõ.",
            "language": language,
        }

    except sr.RequestError as e:
        error_msg = str(e)
        if "403" in error_msg or "401" in error_msg:
            error_msg = "Google Speech Recognition service error - please try again later"

        return {
            "status": "error",
            "error": f"Speech Recognition error: {error_msg}",
            "language": language,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Audio processing error: {str(e)}",
            "language": language,
        }

    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"🗑️ Cleaned up temp file: {temp_file}")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete temp file {temp_file}: {e}")


async def transcribe_audio(
    audio_data: bytes,
    language: str = "vi",
    audio_format: Optional[str] = "webm",
) -> Dict[str, str]:
    return await asyncio.to_thread(
        transcribe_audio_sync,
        audio_data,
        language,
        audio_format,
    )


def list_supported_languages() -> Dict[str, str]:
    """List all supported languages for STT"""
    return LANGUAGE_CODES
    