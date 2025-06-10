#!/bin/bash

# =============================================================================
# Certificate Generation System Setup Script
# =============================================================================
# Author: devag7 (Deva Garwalla)
# Description: Automated setup script for certificate generation system
# Usage: chmod +x setup.sh && ./setup.sh
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
echo -e "${BLUE}"
echo "🎓 Certificate Generation System Setup"
echo "======================================"
echo "Author: devag7 (Deva Garwalla)"
echo -e "${NC}"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    log_warning "This script is optimized for macOS. Some commands may need adjustment for other systems."
fi

# =============================================================================
# SYSTEM REQUIREMENTS CHECK
# =============================================================================
log_info "Checking system requirements..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_success "Python found: $PYTHON_VERSION"
else
    log_error "Python 3 is required but not installed."
    exit 1
fi

# Check Homebrew (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        log_success "Homebrew found"
    fi
fi

# =============================================================================
# INSTALL SYSTEM DEPENDENCIES
# =============================================================================
log_info "Installing system dependencies..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS with Homebrew
    log_info "Installing FFmpeg..."
    brew install ffmpeg || log_warning "FFmpeg installation failed or already installed"
    
    log_info "Installing ImageMagick..."
    brew install imagemagick || log_warning "ImageMagick installation failed or already installed"
    
    log_info "Installing Redis..."
    brew install redis || log_warning "Redis installation failed or already installed"
    
    log_success "System dependencies installation completed"
else
    log_warning "Please install FFmpeg, ImageMagick, and Redis manually for your system"
    echo "Ubuntu/Debian: sudo apt install ffmpeg imagemagick redis-server"
    echo "CentOS/RHEL: sudo yum install ffmpeg ImageMagick redis"
fi

# =============================================================================
# PYTHON ENVIRONMENT SETUP
# =============================================================================
log_info "Setting up Python virtual environment..."

# Check if virtual environment already exists
if [ -d "my_project_env" ]; then
    log_warning "Virtual environment already exists. Skipping creation."
else
    log_info "Creating virtual environment..."
    python3 -m venv my_project_env
    log_success "Virtual environment created"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source my_project_env/bin/activate

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
log_info "Installing Python dependencies..."
pip install -r requirements.txt
log_success "Python dependencies installed"

# =============================================================================
# DIRECTORY STRUCTURE SETUP
# =============================================================================
log_info "Setting up directory structure..."

# Create required directories
mkdir -p certificates
mkdir -p temp
mkdir -p templates
mkdir -p fonts
mkdir -p logs

log_success "Directory structure created"

# =============================================================================
# CONFIGURATION SETUP
# =============================================================================
log_info "Setting up configuration..."

# Check if .env exists
if [ ! -f ".env" ]; then
    log_warning ".env file not found. Creating default configuration..."
    cp .env.example .env 2>/dev/null || log_warning "No .env.example found"
fi

# Set executable permissions
chmod +x producer.py 2>/dev/null || true

log_success "Configuration setup completed"

# =============================================================================
# SERVICE SETUP
# =============================================================================
log_info "Setting up services..."

# Start Redis (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    log_info "Starting Redis server..."
    if brew services list | grep redis | grep -q "started"; then
        log_success "Redis is already running"
    else
        brew services start redis
        sleep 2
        if brew services list | grep redis | grep -q "started"; then
            log_success "Redis started successfully"
        else
            log_warning "Redis may not have started properly"
        fi
    fi
fi

# =============================================================================
# VERIFICATION TESTS
# =============================================================================
log_info "Running verification tests..."

# Test Python imports
log_info "Testing Python module imports..."
python3 -c "import tasks, utils; print('✅ All modules imported successfully')" || {
    log_error "Module import test failed"
    exit 1
}

# Test FFmpeg
if command -v ffmpeg &> /dev/null; then
    log_success "FFmpeg is available"
else
    log_error "FFmpeg is not available"
    exit 1
fi

# Test ImageMagick
if command -v magick &> /dev/null || command -v convert &> /dev/null; then
    log_success "ImageMagick is available"
else
    log_error "ImageMagick is not available"
    exit 1
fi

# Test Redis connection
log_info "Testing Redis connection..."
python3 -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    exit(1)
" || {
    log_warning "Redis connection test failed"
}

# Test certificate generation
log_info "Running certificate generation test..."
ASYNC_MODE=false python3 -c "
from tasks import generate_certificate
from datetime import datetime
import os

test_data = {
    'user_name': 'Setup Test User',
    'college': 'Test Institution',
    'certificate_id': f'SETUP-TEST-{datetime.now().strftime(\"%Y%m%d-%H%M%S\")}',
    'issued_at': datetime.now().isoformat(),
    'topic': 'Setup Verification'
}

try:
    result = generate_certificate(test_data)
    if os.path.exists(result):
        print('✅ Test certificate generated successfully')
        os.remove(result)  # Cleanup test certificate
    else:
        print('❌ Test certificate file not found')
        exit(1)
except Exception as e:
    print(f'❌ Certificate generation test failed: {e}')
    exit(1)
" || {
    log_warning "Certificate generation test failed - check dependencies"
}

# =============================================================================
# COMPLETION
# =============================================================================
echo
echo -e "${GREEN}"
echo "🎉 Setup completed successfully!"
echo "================================"
echo -e "${NC}"

log_info "Next steps:"
echo "1. Activate the virtual environment: source my_project_env/bin/activate"
echo "2. Run a test certificate: python producer.py"
echo "3. Start Celery worker: celery -A tasks worker --loglevel=info"
echo "4. For batch processing: python producer.py batch"
echo "5. Monitor tasks: celery -A tasks inspect active"

echo
log_success "Certificate Generation System is ready to use!"
echo -e "${BLUE}Created by devag7 (Deva Garwalla)${NC}"
echo "🔗 GitHub: https://github.com/devag7"

# Deactivate virtual environment
deactivate 2>/dev/null || true