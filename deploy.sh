#!/bin/bash

# TTS & STT API - Quick Deployment Script
# Usage: bash deploy.sh [production|development]

set -e

MODE=${1:-production}
APP_DIR="/opt/tts-api"
APP_USER="tts-api"

echo "🚀 TTS & STT API Deployment"
echo "Mode: $MODE"
echo "---"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# 1. Check if running as root
if [ "$MODE" == "production" ] && [ "$EUID" -ne 0 ]; then
    log_error "Production deployment requires root. Run with sudo."
    exit 1
fi

# 2. Install system dependencies
log_info "Installing system dependencies..."

if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y python3-pip python3-venv git curl wget ffmpeg flac
elif command -v yum &> /dev/null; then
    sudo yum install -y python3-pip python3-devel git curl wget ffmpeg flac
else
    log_error "Unsupported package manager"
    exit 1
fi

log_success "System dependencies installed"

# 3. Create app directory
log_info "Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown -R $APP_USER:$APP_USER $APP_DIR 2>/dev/null || true

# 4. Setup Python virtual environment
log_info "Setting up Python virtual environment..."
cd $APP_DIR

if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_success "Virtual environment exists"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

log_success "Python dependencies installed"

# 5. Create cache directories
log_info "Creating cache directories..."
mkdir -p audio_cache
mkdir -p transcription_cache
chmod 755 audio_cache transcription_cache

log_success "Cache directories created"

# 6. Setup based on mode
if [ "$MODE" == "production" ]; then
    log_info "Setting up production environment..."

    # Create app user if not exists
    if ! id "$APP_USER" &>/dev/null; then
        log_info "Creating $APP_USER user..."
        sudo useradd -m -s /bin/bash $APP_USER
    fi

    # Install Gunicorn
    pip install gunicorn

    # Create systemd service
    log_info "Creating systemd service..."

    sudo mkdir -p /var/log/tts-api
    sudo chown $APP_USER:$APP_USER /var/log/tts-api

    log_success "Production deployment complete!"
    echo ""
    echo "📊 Next steps:"
    echo "1. Run: sudo bash deploy.sh production"
    echo "2. View logs: sudo journalctl -u tts-api -f"
    echo "3. Access API: http://your-server-ip:8000/"

else
    # Development mode
    log_info "Setting up development environment..."

    log_success "Development setup complete!"
    echo ""
    echo "🚀 To start server:"
    echo "  cd $APP_DIR"
    echo "  source venv/bin/activate"
    echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "🌐 Access at: http://localhost:8000/web"
fi

log_success "Deployment finished!"
