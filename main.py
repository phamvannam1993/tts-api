from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import asyncio
import os

from tts_service import generate_audio, VOICE_PRESETS

app = FastAPI(
    title="TTS API - Free Text-to-Speech",
    description="Edge TTS - Hoàn toàn FREE, không cần credentials. Hỗ trợ 50+ giọng nói, 20+ ngôn ngữ"
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
# API: Convert text -> audio
# -----------------------
@app.post("/tts")
async def tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    # Validate voice exists
    if req.voice not in VOICE_PRESETS:
        raise HTTPException(status_code=400, detail=f"Voice '{req.voice}' not found")

    try:
        file_path = await generate_audio(
            req.text,
            req.voice,
            req.rate,
            req.pitch
        )

        return FileResponse(
            path=file_path,
            media_type="audio/mpeg",
            filename="speech.mp3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------
# API: list all voices with details
# -----------------------
@app.get("/voices")
def list_voices():
    """List all available voices with metadata"""
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
    """Get details for a specific voice"""
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
# health check
# -----------------------
@app.get("/")
def home():
    return {
        "status": "TTS API running ✅",
        "version": "3.0",
        "provider": "Edge TTS (Hoàn toàn FREE)",
        "voices": "50+ giọng, 20+ ngôn ngữ",
        "credentials_needed": False,
        "docs": "/docs",
        "web": "/web"
    }


# -----------------------
# Serve static files (web UI)
# -----------------------
if os.path.exists("static"):
    app.mount("/web", StaticFiles(directory="static", html=True), name="static")