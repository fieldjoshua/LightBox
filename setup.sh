#!/bin/bash

# LightBox LED Matrix Project Setup Script
# For Raspberry Pi OS (Bookworm) with Python 3.11+

set -e

echo "🌟 Setting up LightBox LED Matrix Project..."

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

if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 0 ]]; then
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

# Install dependencies
echo "📦 Installing dependencies..."
pip install \
    adafruit-blinka \
    adafruit-circuitpython-neopixel \
    RPi.GPIO \
    flask \
    flask-cors \
    pillow \
    numpy \
    psutil

# Create requirements.txt
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

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: source venv/bin/activate"
echo "2. Run: sudo ./venv/bin/python3 CosmicLED.py"
echo "3. Access web interface at http://localhost:5000"
echo ""
echo "To enable auto-start on boot:"
echo "sudo systemctl enable lightbox.service"
echo "sudo systemctl start lightbox.service"