#!/bin/bash

# LightBox LED Matrix Project Setup Script - MINIMAL VERSION
# Optimized for Raspberry Pi Zero W

set -e

echo "🌟 Setting up LightBox LED Matrix Project (Minimal)..."

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi OS"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "📍 Detected Python $python_version"

# Simple version check without bc
major=$(echo $python_version | cut -d. -f1)
minor=$(echo $python_version | cut -d. -f2)

if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 11 ]); then
    echo "❌ Python 3.11+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install minimal dependencies
echo "📦 Installing minimal dependencies..."
pip install -r requirements-minimal.txt

# Create requirements.txt from installed packages
echo "📄 Creating requirements.txt..."
pip freeze > requirements.txt

# Set permissions for GPIO access
echo "🔐 Setting up GPIO permissions..."
if ! groups $USER | grep -q gpio; then
    echo "Adding user to gpio group..."
    sudo usermod -a -G gpio $USER
    echo "⚠️  Please log out and log back in for GPIO group changes to take effect"
fi

# Create systemd service directory if needed
sudo mkdir -p /etc/systemd/system

echo "✅ Minimal setup complete!"
echo ""
echo "Optimizations for Pi Zero W:"
echo "- Reduced dependencies (~50MB vs ~200MB)"
echo "- OLED display disabled (saves 10MB)"
echo "- System monitoring disabled"
echo "- Faster startup time"
echo ""
echo "Next steps:"
echo "1. Log out and back in (if first run)"
echo "2. Run: source venv/bin/activate"
echo "3. Run: sudo ./venv/bin/python3 CosmicLED.py"
echo "4. Access web interface at http://$(hostname -I | cut -d' ' -f1):5000"
echo ""
echo "To enable auto-start on boot:"
echo "sudo cp lightbox.service /etc/systemd/system/"
echo "sudo systemctl enable lightbox.service"