#!/bin/bash
# Raspberry Pi GPIO Fix Script
# Fixes the Jetson GPIO conflict on Raspberry Pi

echo "🔧 Fixing Raspberry Pi GPIO libraries..."
echo "This will remove conflicting packages and install correct ones"

# Check if we're on a Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script is for Raspberry Pi only!"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Remove ALL conflicting GPIO packages
echo "🗑️  Removing conflicting GPIO packages..."
pip uninstall -y Jetson.GPIO RPi.GPIO adafruit-blinka adafruit-circuitpython-neopixel rpi-ws281x

# Clean pip cache
echo "🧹 Cleaning pip cache..."
pip cache purge

# Install system GPIO packages first
echo "📦 Installing system GPIO packages..."
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio python3-dev

# Install correct Python packages in specific order
echo "📦 Installing correct GPIO packages..."
pip install --no-cache-dir RPi.GPIO
pip install --no-cache-dir adafruit-blinka
pip install --no-cache-dir adafruit-circuitpython-neopixel
pip install --no-cache-dir rpi-ws281x

# Install web dependencies
echo "📦 Installing web dependencies..."
pip install --no-cache-dir flask flask-cors

echo "✅ GPIO fix complete!"
echo ""
echo "Now try running LightBox:"
echo "  python3 CosmicLED.py"
echo ""
echo "If you still have issues, try:"
echo "  python3 run_simulation.py" 