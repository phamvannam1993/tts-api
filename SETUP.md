# 🚀 TTS API - Server Setup Guide

## 1. Dependencies cần cài

### System packages (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

### Python version:
```
Python 3.9+ (recommended 3.10+)
```

## 2. Clone & Setup

```bash
# Clone repo
cd /var/www
git clone <your-repo-url> tts-api
cd tts-api

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

## 3. Cài Systemd Service

### Tạo service file:
```bash
sudo nano /etc/systemd/system/tts-api.service
```

Paste nội dung:
```ini
[Unit]
Description=TTS API Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/tts-api
Environment="PATH=/var/www/tts-api/venv/bin"
ExecStart=/var/www/tts-api/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=append:/var/log/tts-api.log
StandardError=append:/var/log/tts-api.log

[Install]
WantedBy=multi-user.target
```

### Kích hoạt service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tts-api
sudo systemctl start tts-api
sudo systemctl status tts-api
```

### Xem logs:
```bash
sudo tail -f /var/log/tts-api.log
```

## 4. Nginx Reverse Proxy (Optional)

### Tạo config:
```bash
sudo nano /etc/nginx/sites-available/tts-api
```

Paste:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
    }
}
```

### Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/tts-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 5. File & Directory Structure

```
/var/www/tts-api/
├── main.py
├── tts_service.py
├── cleanup_scheduler.py
├── requirements.txt
├── deploy.sh
├── static/
│   └── index.html
├── audio_cache/      # Tự tạo (nơi lưu audio files)
│   ├── cache.json    # Tự tạo (cache mapping)
│   └── *.mp3         # Audio files
└── venv/            # Virtual environment
```

### Tạo audio_cache directory:
```bash
mkdir -p /var/www/tts-api/audio_cache
sudo chown www-data:www-data /var/www/tts-api/audio_cache
sudo chmod 755 /var/www/tts-api/audio_cache
```

## 6. Permissions

```bash
# Set ownership
sudo chown -R www-data:www-data /var/www/tts-api

# Set permissions
sudo chmod -R 755 /var/www/tts-api
sudo chmod -R 775 /var/www/tts-api/audio_cache
```

## 7. Quick Deploy

```bash
# Tính năng deploy.sh có sẵn
cd /var/www/tts-api
chmod +x deploy.sh
./deploy.sh
```

hoặc manual:
```bash
cd /var/www/tts-api
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart tts-api
```

## 8. Test API

```bash
# Health check
curl http://your-domain.com/

# Generate audio
curl -X POST http://your-domain.com/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào"}'

# List voices
curl http://your-domain.com/voices
```

## 9. SSL/HTTPS (with Certbot)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo systemctl restart nginx
```

## 10. Troubleshooting

### Port 8000 already in use:
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Permission denied:
```bash
sudo chown -R www-data:www-data /var/www/tts-api
```

### Service won't start:
```bash
sudo systemctl status tts-api
sudo journalctl -u tts-api -n 50
```

### Check logs:
```bash
sudo tail -100 /var/log/tts-api.log
```

## 11. Monitoring

### Add to crontab for monitoring:
```bash
# Check every 5 minutes
*/5 * * * * systemctl is-active --quiet tts-api || systemctl start tts-api
```

---

**Notes:**
- Audio cache tự động xóa files cũ >1 giờ mỗi 1 giờ
- Cache mapping lưu trong `audio_cache/cache.json`
- Static files (web UI) phục vụ từ `/web` endpoint
