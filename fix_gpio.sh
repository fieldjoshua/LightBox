#!/bin/bash
# LightBox GPIO Fix Script
# Resolves GPIO library conflicts and installs correct dependencies

echo "🔧 Fixing LightBox GPIO dependencies..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Uninstall problematic packages
echo "🗑️  Removing conflicting GPIO packages..."
pip uninstall -y Jetson.GPIO RPi.GPIO adafruit-blinka

# Install correct packages for Raspberry Pi
echo "📦 Installing correct GPIO packages..."
pip install RPi.GPIO adafruit-blinka rpi-ws281x

# Alternative: Install minimal requirements
echo "📦 Installing minimal requirements..."
pip install -r requirements-minimal.txt

echo "✅ GPIO fix complete!"
echo ""
echo "Now try running LightBox:"
echo "  python3 CosmicLED.py"
echo ""
echo "Or run in simulation mode:"
echo "  python3 run_simulation.py" 