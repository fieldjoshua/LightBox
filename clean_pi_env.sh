#!/bin/bash
# Clean up Python environment for CosmicLED on Raspberry Pi
# Usage: source venv/bin/activate && bash clean_pi_env.sh

set -e

# Uninstall problematic and unnecessary packages
pip uninstall -y Jetson.GPIO lgpio binho-host-adapter pyftdi pyusb adafruit-circuitpython-connectionmanager adafruit-circuitpython-requests pytest iniconfig pluggy Pygments pillow adafruit-circuitpython-ssd1306 adafruit-circuitpython-framebuf

# Reinstall essentials
pip install --force-reinstall RPi.GPIO adafruit-blinka adafruit-circuitpython-neopixel Flask flask-cors numpy psutil

# Verify Jetson.GPIO is gone
if pip show Jetson.GPIO > /dev/null 2>&1; then
    echo "❌ Jetson.GPIO is still installed! Please uninstall manually."
else
    echo "✅ Jetson.GPIO is not installed."
fi

echo "✅ Environment cleanup complete. Try running your program again." 