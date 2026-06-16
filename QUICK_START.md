# ⚡ Quick Start - Server Deploy

## 🔧 Cài đặt (5 phút)

```bash
# 1. SSH vào server
ssh user@your-server.com

# 2. Clone repo
cd /var/www
git clone <repo-url> tts-api
cd tts-api

# 3. Setup Python venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Tạo audio_cache directory
mkdir -p audio_cache
chmod 755 audio_cache

# 5. Test chạy local
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000
# Truy cập: http://localhost:8000/
# Ngừng: Ctrl+C
```

## 🚀 Setup Systemd (để chạy như service)

```bash
# 1. Tạo service file
sudo bash -c 'cat > /etc/systemd/system/tts-api.service << "EOF"
[Unit]
Description=TTS API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/tts-api
Environment="PATH=/var/www/tts-api/venv/bin"
ExecStart=/var/www/tts-api/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'

# 2. Enable & start
sudo systemctl daemon-reload
sudo systemctl enable tts-api
sudo systemctl start tts-api

# 3. Kiểm tra status
sudo systemctl status tts-api

# 4. Xem logs
sudo journalctl -u tts-api -f
```

## 🌐 Setup Nginx (Reverse Proxy)

```bash
# 1. Tạo nginx config
sudo bash -c 'cat > /etc/nginx/sites-available/tts-api << "EOF"
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF'

# 2. Enable site
sudo ln -s /etc/nginx/sites-available/tts-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## ✅ Test API

```bash
# Health check
curl http://your-domain.com/

# Generate TTS
curl -X POST http://your-domain.com/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào"}'

# Get voices
curl http://your-domain.com/voices

# Web UI
http://your-domain.com/web/
```

## 📝 Common Commands

```bash
# Start service
sudo systemctl start tts-api

# Stop service
sudo systemctl stop tts-api

# Restart
sudo systemctl restart tts-api

# View logs (last 50 lines)
sudo journalctl -u tts-api -n 50

# View logs (real-time)
sudo journalctl -u tts-api -f

# Check if running
sudo systemctl is-active tts-api

# Enable auto-start on boot
sudo systemctl enable tts-api

# Disable auto-start
sudo systemctl disable tts-api
```

## 🔄 Update Code

```bash
cd /var/www/tts-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart tts-api
```

hoặc dùng script:
```bash
cd /var/www/tts-api
chmod +x deploy.sh
./deploy.sh
```

## 📊 Monitoring

```bash
# Check disk usage
du -sh /var/www/tts-api/audio_cache/

# Check service memory
ps aux | grep tts-api

# Check port usage
sudo lsof -i :8000
```

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| Port 8000 in use | `sudo lsof -i :8000` → kill PID |
| Service won't start | `sudo journalctl -u tts-api -n 50` |
| Permission denied | `sudo chown -R www-data:www-data /var/www/tts-api` |
| 502 Bad Gateway | Check nginx logs: `sudo tail /var/log/nginx/error.log` |

---

**More details:** Xem file `SETUP.md`
