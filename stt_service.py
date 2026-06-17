import speech_recognition as sr
import os
import hashlib
import json
from typing import Optional, Dict
import io
import wave
import subprocess
import tempfile

TRANSCRIPTION_CACHE_DIR = "transcription_cache"
TRANSCRIPTION_CACHE_FILE = os.path.join(TRANSCRIPTION_CACHE_DIR, "cache.json")

os.makedirs(TRANSCRIPTION_CACHE_DIR, exist_ok=True)

# Initialize recognizer
recognizer = sr.Recognizer()

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
    "vi": "vi-VN",      # Vietnamese
    "en": "en-US",      # English
    "es": "es-ES",      # Spanish
    "fr": "fr-FR",      # French
    "de": "de-DE",      # German
    "it": "it-IT",      # Italian
    "pt": "pt-PT",      # Portuguese
    "ru": "ru-RU",      # Russian
    "ja": "ja-JP",      # Japanese
    "zh": "zh-CN",      # Chinese (Simplified)
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


def convert_to_wav_with_ffmpeg(input_path: str, output_path: str) -> bool:
    """Convert audio file to WAV using ffmpeg"""
    try:
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"⚠️ FFmpeg error: {result.stderr}")
            return False

        print(f"✅ Converted to WAV: {output_path}")
        return True
    except Exception as e:
        print(f"⚠️ Conversion error: {e}")
        return False


def convert_audio_to_wav(audio_data: bytes, format: str) -> bytes:
    """Convert audio data to WAV format"""
    try:
        # If already WAV, return as-is
        if format.lower() == 'wav':
            return audio_data

        # Try to use ffmpeg for conversion
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp_input:
            tmp_input.write(audio_data)
            tmp_input_path = tmp_input.name

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_output:
            tmp_output_path = tmp_output.name

        try:
            # Convert using ffmpeg
            success = convert_to_wav_with_ffmpeg(tmp_input_path, tmp_output_path)

            if not success:
                print(f"⚠️ FFmpeg conversion failed, trying alternative method...")
                raise Exception("FFmpeg conversion failed")

            # Read converted WAV file
            with open(tmp_output_path, 'rb') as f:
                wav_data = f.read()

            return wav_data
        finally:
            # Clean up temp files
            for path in [tmp_input_path, tmp_output_path]:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except:
                    pass

    except Exception as e:
        print(f"⚠️ Audio conversion failed: {e}")
        raise Exception(f"Could not convert audio to WAV format: {str(e)}")


async def transcribe_audio(
    audio_data: bytes,
    language: str = "vi",
    audio_format: str = "mp3"
) -> Dict[str, str]:
    """
    Transcribe audio file to text using Google Speech Recognition

    Args:
        audio_data: Raw audio bytes
        language: Language code (vi, en, es, etc.)
        audio_format: Audio format (mp3, wav, etc.)

    Returns:
        {
            "status": "success",
            "text": "transcribed text",
            "language": "vi"
        }
    """
    temp_file = None
    try:
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
                "cached": True
            }

        # Convert to WAV if needed (SpeechRecognition works best with WAV)
        print(f"🎤 Processing audio file ({audio_format})...")
        if audio_format.lower() != 'wav':
            print(f"🔄 Converting {audio_format.upper()} to WAV...")
            try:
                audio_data = convert_audio_to_wav(audio_data, audio_format.lower())
                audio_format = 'wav'
            except Exception as e:
                # If conversion fails, try using the original format
                print(f"⚠️ Conversion failed, attempting with original format: {e}")

        # Save audio to temporary file for speech_recognition to use
        with tempfile.NamedTemporaryFile(suffix=f".{audio_format.lower()}", delete=False) as tmp:
            tmp.write(audio_data)
            temp_file = tmp.name

        # Load audio using speech_recognition AudioFile
        print(f"📖 Reading audio from temp file...")
        with sr.AudioFile(temp_file) as source:
            audio = recognizer.record(source)

        # Get language code for Google Speech Recognition
        lang_code = LANGUAGE_CODE_MAP.get(language, "vi-VN")

        # Transcribe using Google Speech Recognition
        print(f"🔍 Transcribing audio ({language})...")
        text = recognizer.recognize_google(audio, language=lang_code)

        # Save to cache
        cache[cache_key] = {
            "text": text,
            "language": language,
            "audio_hash": audio_hash
        }
        save_transcription_cache(cache)

        print(f"✅ Transcription complete: {text[:50]}...")

        return {
            "status": "success",
            "text": text,
            "language": language,
            "cached": False
        }

    except sr.UnknownValueError:
        return {
            "status": "error",
            "error": "Could not understand audio - please check file quality or try a different audio",
            "language": language
        }
    except sr.RequestError as e:
        error_msg = str(e)
        if "403" in error_msg or "401" in error_msg:
            error_msg = "Google Speech Recognition service error - please try again later"
        return {
            "status": "error",
            "error": f"Speech Recognition error: {error_msg}",
            "language": language
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Audio processing error: {str(e)}",
            "language": language
        }
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                print(f"🗑️  Cleaned up temp file: {temp_file}")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete temp file {temp_file}: {e}")


def list_supported_languages() -> Dict[str, str]:
    """List all supported languages for STT"""
    return LANGUAGE_CODES
