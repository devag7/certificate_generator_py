#!/bin/bash
# 🎓 Certificate Generator Setup Script
# Author: devag7 (Dev Agarwalla)

echo "🎓 Certificate Generator Setup"
echo "Created by devag7 (Dev Agarwalla)"
echo "=============================="
echo

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found"
else
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if FFmpeg is available
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg found"
else
    echo "❌ FFmpeg not found. Please install FFmpeg"
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
    exit 1
fi

# Check if ImageMagick is available
if command -v convert &> /dev/null || command -v magick &> /dev/null; then
    echo "✅ ImageMagick found"
else
    echo "❌ ImageMagick not found. Please install ImageMagick"
    echo "   macOS: brew install imagemagick"
    echo "   Ubuntu: sudo apt install imagemagick"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install requirements
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p certificates
mkdir -p temp

echo
echo "🎉 Setup complete!"
echo "✅ All dependencies installed"
echo "✅ Directories created"
echo
echo "🚀 Ready to generate certificates!"
echo "   Run: python producer.py"
echo