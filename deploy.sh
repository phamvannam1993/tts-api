#!/bin/bash

cd /var/www/tts-api || exit

echo "Pull code mới..."
git pull origin main

echo "Kích hoạt venv..."
source venv/bin/activate

echo "Cài dependencies nếu có requirements.txt..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "Restart service..."
sudo systemctl restart tts-api

echo "Kiểm tra service..."
sudo systemctl status tts-api --no-pager

echo "Done."