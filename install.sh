#!/bin/bash

echo "🚀 Installing YouTube Reaction Bot Dependencies..."

# Update system
echo "📦 Updating system packages..."
sudo apt update

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y python3-pip python3-venv ffmpeg

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip3 install -r requirements.txt

# Install optional dependencies (comment out if not needed)
echo "✨ Installing optional features..."
# pip3 install -r requirements-optional.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p downloads
mkdir -p shorts
mkdir -p credentials
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x auto_youtube_bot.py

echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Add your API keys to .env file"
echo "2. Run: python3 auto_youtube_bot.py"
echo ""
echo "🎬 Your reaction shorts bot is ready!"
