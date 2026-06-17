# TTS & STT API - Chuyển Đổi Text ↔ Âm Thanh

## 🎯 Tổng Quan

API này cung cấp hai tính năng chính:
- **TTS (Text-to-Speech)**: Chuyển văn bản thành âm thanh
- **STT (Speech-to-Text)**: Chuyển âm thanh thành văn bản

**100% FREE** - không cần API keys hoặc credentials

## 📦 Công Nghệ

- **Backend**: FastAPI (Python)
- **TTS Provider**: Microsoft Edge TTS (50+ giọng, 20+ ngôn ngữ)
- **STT Provider**: Google Speech Recognition (10+ ngôn ngữ)
- **Frontend**: Vanilla JavaScript + HTML/CSS

## 🚀 Cài Đặt

### 1. Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies bắt buộc**:
- `fastapi==0.104.1`
- `uvicorn==0.24.0`
- `edge-tts==6.1.3` (TTS)
- `SpeechRecognition==3.10.1` (STT)
- `python-multipart==0.0.6`
- `apscheduler==3.10.4`

### 2. Cài Đặt FLAC (bắt buộc cho STT)

**macOS**:
```bash
brew install flac
```

**Linux (Ubuntu/Debian)**:
```bash
apt-get install flac
```

**Windows**:
Tải từ: https://xiph.org/flac/download.html

### 3. Chạy Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Truy cập: http://localhost:8000/web

## 📚 API Endpoints

### TTS Endpoints

#### POST `/tts` - Tạo âm thanh từ text

**Request**:
```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Xin chào, đây là bài kiểm tra.",
    "voice": "vi-VN-HoaiMyNeural",
    "rate": "+0%",
    "pitch": "+0Hz"
  }'
```

**Response**:
```json
{
  "status": "success",
  "audio_url": "/audio/tts_abc123.mp3",
  "filename": "tts_abc123.mp3"
}
```

#### GET `/voices` - Lấy danh sách giọng nói

```bash
curl http://localhost:8000/voices
```

#### GET `/voices/{voice_id}` - Chi tiết giọng nói

```bash
curl http://localhost:8000/voices/vi-VN-HoaiMyNeural
```

### STT Endpoints

#### POST `/stt` - Chuyển âm thanh thành text

**Request**:
```bash
curl -X POST http://localhost:8000/stt?language=vi&audio_format=mp3 \
  -F "file=@audio.mp3"
```

**Response** (Success):
```json
{
  "status": "success",
  "text": "Xin chào, đây là bài kiểm tra.",
  "language": "vi",
  "cached": false
}
```

**Response** (Error):
```json
{
  "status": "error",
  "error": "Could not understand audio",
  "language": "vi"
}
```

**Parameters**:
- `language` (default: `vi`): Mã ngôn ngữ
- `audio_format` (default: `mp3`): Định dạng file âm thanh

#### GET `/stt/languages` - Danh sách ngôn ngữ hỗ trợ

```bash
curl http://localhost:8000/stt/languages
```

**Response**:
```json
{
  "supported_languages": {
    "vi": "Vietnamese",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "zh": "Chinese"
  }
}
```

## 🎵 Giọng Nói TTS Hỗ Trợ

### Tiếng Việt (Edge TTS)

**Nữ - Hoài My**:
- `vi-VN-HoaiMyNeural` - Bình thường
- `vi-VN-HoaiMyNeural-slow` - Đọc chậm
- `vi-VN-HoaiMyNeural-veryslow` - Rất chậm
- `vi-VN-HoaiMyNeural-story` - Giọng mềm

**Nam - Nam Minh**:
- `vi-VN-NamMinhNeural` - Bình thường
- `vi-VN-NamMinhNeural-slow` - Đọc chậm
- `vi-VN-NamMinhNeural-veryslow` - Rất chậm

Xem `/voices` endpoint để danh sách đầy đủ các giọng nói

## 🎙️ Ngôn Ngữ STT Hỗ Trợ

| Code | Ngôn Ngữ |
|------|---------|
| `vi` | Tiếng Việt |
| `en` | English |
| `es` | Español |
| `fr` | Français |
| `de` | Deutsch |
| `it` | Italiano |
| `pt` | Português |
| `ru` | Русский |
| `ja` | 日本語 |
| `zh` | 中文 |

## ⚙️ Cấu Hình

Các biến môi trường tùy chỉnh (trong `main.py`):

```python
# TTS
TTS_API_URL = "https://api-v2.behayhoc.com/tts"  # External API
AUDIO_CACHE_DIR = "audio_cache"  # Thư mục lưu cache
CLEANUP_INTERVAL = 60  # Minutes

# STT
TRANSCRIPTION_CACHE_DIR = "transcription_cache"
TRANSCRIPTION_CACHE_FILE = "transcription_cache/cache.json"
```

## 📁 Cấu Trúc Thư Mục

```
songtute/tts-api/
├── main.py                      # FastAPI application
├── tts_service.py              # TTS service logic
├── stt_service.py              # STT service logic (NEW)
├── cleanup_scheduler.py        # Auto-cleanup old files
├── requirements.txt            # Python dependencies
├── README_STT.md              # This file (NEW)
├── static/
│   └── index.html             # Web UI (UPDATED)
├── audio_cache/               # TTS audio files
└── transcription_cache/       # STT cached results (NEW)
```

## 🔒 Bảo Mật

- ✅ Ngăn chặn directory traversal attacks
- ✅ Xác thực định dạng file
- ✅ Rate limiting (tuỳ chỉnh)
- ✅ CORS middleware bảo vệ
- ✅ Validation đầu vào

## 📊 Performance

- **TTS**: ~1-3 giây per request (phụ thuộc text length)
- **STT**: ~2-5 giây per request (phụ thuộc audio length)
- **Caching**: Instant (<100ms) cho kết quả cached

## 🐛 Troubleshooting

### STT không hoạt động
**Lỗi**: `FLAC conversion utility not available`
**Giải pháp**: Cài đặt FLAC (xem mục Cài Đặt)

### TTS API lỗi kết nối
**Lỗi**: `Could not connect to TTS API`
**Giải pháp**: Kiểm tra kết nối internet hoặc proxy settings

### File quá lớn
**Lỗi**: `413 Payload Too Large`
**Giải pháp**: Giảm kích thước file âm thanh (<25MB khuyên cáo)

## 📝 Ghi Chú

- Tất cả dữ liệu cache được lưu locally, không lên server
- STT cache được tự động dọn dẹp mỗi 60 phút
- Google Speech Recognition cần kết nối internet
- Chất lượng STT phụ thuộc vào chất lượng audio input

## 🤝 Đóng Góp

Để cải tiến STT:
1. Thêm thêm ngôn ngữ trong `LANGUAGE_CODE_MAP` (stt_service.py)
2. Tối ưu audio preprocessing
3. Thêm support cho TTS/STT providers khác

## 📄 License

100% Free & Open Source

---

**Version**: 4.0  
**Last Updated**: 2026-06-17
