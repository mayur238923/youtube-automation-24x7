#!/data/data/com.termux/files/usr/bin/bash

echo "📱 Installing YouTube Bot for Termux..."

# Update Termux packages
echo "📦 Updating Termux packages..."
pkg update && pkg upgrade -y

# Install essential packages
echo "🔧 Installing system packages..."
pkg install -y python python-pip git ffmpeg

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install -r requirements-termux.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p downloads
mkdir -p shorts  
mkdir -p credentials
mkdir -p logs

# Set permissions
chmod +x auto_youtube_bot.py

echo "✅ Termux installation complete!"
echo ""
echo "⚠️  Termux Limitations:"
echo "- MoviePy may not work properly"
echo "- OpenCV might have issues"
echo "- Use lightweight video processing"
echo ""
echo "🚀 To run: python auto_youtube_bot.py"
