#!/bin/bash
# Quick LightBox GPIO Fix - One command to fix everything

echo "🚀 Quick LightBox GPIO Fix Starting..."

# Create/activate virtual environment
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate

# Remove all conflicting packages (ignore errors)
pip uninstall -y Jetson.GPIO RPi.GPIO adafruit-blinka adafruit-circuitpython-neopixel rpi-ws281x 2>/dev/null || true

# Install system packages
sudo apt-get update && sudo apt-get install -y python3-rpi.gpio python3-dev

# Install Python packages
pip install --no-cache-dir RPi.GPIO adafruit-blinka rpi-ws281x flask flask-cors

echo "✅ Fix complete! Now run: python3 Conductor.py"

source venv/bin/activate
python3 Conductor.py 