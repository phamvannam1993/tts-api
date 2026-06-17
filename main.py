from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from contextlib import asynccontextmanager

from tts_service import generate_audio, VOICE_PRESETS
from stt_service import transcribe_audio, list_supported_languages
from cleanup_scheduler import start_cleanup_scheduler

scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    scheduler = start_cleanup_scheduler(interval_minutes=60)
    yield
    if scheduler and scheduler.running:
        scheduler.shutdown()
        print("✅ Cleanup Scheduler stopped")


app = FastAPI(
    title="TTS & STT API - Text-to-Speech & Speech-to-Text",
    description="Edge TTS + STT - Hoàn toàn FREE, không cần credentials. TTS: 50+ giọng, 20+ ngôn ngữ. STT: Google Speech Recognition, hỗ trợ 10+ ngôn ngữ",
    lifespan=lifespan
)

# -----------------------
# CORS - Mở all cho frontend
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Content-Disposition",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ],
)


# -----------------------
# Request model
# -----------------------
class TTSRequest(BaseModel):
    text: str
    voice: str = "vi-VN-HoaiMyNeural"
    rate: Optional[str] = None
    pitch: Optional[str] = None


# -----------------------
# Request model for STT
# -----------------------
class STTRequest(BaseModel):
    language: str = "vi"
    audio_format: str = "mp3"


# -----------------------
# API: Convert text -> audio
# -----------------------
@app.post("/tts")
async def tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    if req.voice not in VOICE_PRESETS:
        raise HTTPException(status_code=400, detail=f"Voice '{req.voice}' not found")

    try:
        file_path = await generate_audio(
            req.text,
            req.voice,
            req.rate,
            req.pitch
        )

        filename = os.path.basename(file_path)

        return {
            "status": "success",
            "audio_url": f"/audio/{filename}",
            "filename": filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------
# API: Download audio file
# -----------------------
@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join("audio_cache", filename)

    # Security: prevent directory traversal
    if not os.path.abspath(file_path).startswith(os.path.abspath("audio_cache")):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename
    )


# -----------------------
# API: list all voices with details
# -----------------------
@app.get("/voices")
def list_voices():
    voices_by_language = {}

    for voice_id, preset in VOICE_PRESETS.items():
        language = preset.get("language", "Unknown")

        if language not in voices_by_language:
            voices_by_language[language] = []

        voices_by_language[language].append({
            "id": voice_id,
            "name": preset.get("name", voice_id),
            "provider": preset.get("provider"),
            "region": preset.get("region"),
            "language": language
        })

    return voices_by_language


# -----------------------
# API: get voice details
# -----------------------
@app.get("/voices/{voice_id}")
def get_voice_details(voice_id: str):
    if voice_id not in VOICE_PRESETS:
        raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")

    preset = VOICE_PRESETS[voice_id]

    return {
        "id": voice_id,
        "name": preset.get("name"),
        "provider": preset.get("provider"),
        "region": preset.get("region"),
        "language_code": preset.get("language_code", "vi-VN")
    }


# -----------------------
# API: Convert audio -> text (STT)
# -----------------------
@app.post("/stt")
async def stt(
    file: UploadFile = File(...),
    language: str = "vi",
    audio_format: str = "mp3"
):
    """
    Transcribe audio file to text

    - **file**: Audio file (mp3, wav, etc.)
    - **language**: Language code (vi, en, es, fr, de, it, pt, ru, ja, zh)
    - **audio_format**: Audio format (mp3, wav, etc.)
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="Audio file is required")

        # Validate language
        supported_langs = list_supported_languages()
        if language not in supported_langs:
            raise HTTPException(
                status_code=400,
                detail=f"Language '{language}' not supported. Supported: {', '.join(supported_langs.keys())}"
            )

        # Read file content
        audio_data = await file.read()
        if not audio_data:
            raise HTTPException(status_code=400, detail="Audio file is empty")

        # Transcribe
        result = await transcribe_audio(audio_data, language, audio_format)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT processing failed: {str(e)}")


# -----------------------
# API: Get supported languages for STT
# -----------------------
@app.get("/stt/languages")
def get_stt_languages():
    """List all supported languages for speech-to-text"""
    return {
        "supported_languages": list_supported_languages()
    }


# -----------------------
# health check
# -----------------------
@app.get("/")
def home():
    return {
        "status": "TTS & STT API running ✅",
        "version": "4.0",
        "features": {
            "tts": {
                "provider": "Edge TTS (FREE)",
                "voices": "50+ giọng",
                "languages": "20+ ngôn ngữ",
                "endpoint": "/tts"
            },
            "stt": {
                "provider": "Google Speech Recognition (FREE)",
                "languages": "10+ ngôn ngữ",
                "endpoint": "/stt"
            }
        },
        "credentials_needed": False,
        "docs": "/docs",
        "web": "/web"
    }


# -----------------------
# Serve static files
# -----------------------
if os.path.exists("static"):
    app.mount("/web", StaticFiles(directory="static", html=True), name="static")
    