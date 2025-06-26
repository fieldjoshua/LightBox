#!/usr/bin/env python3
"""
LightBox GPIO Diagnostic Tool
Helps identify and fix GPIO library conflicts
"""

import sys
import subprocess
import os

def check_platform():
    """Check if we're on a Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' in f.read():
                print("✅ Running on Raspberry Pi")
                return True
    except:
        pass
    print("⚠️  Not running on Raspberry Pi")
    return False

def check_gpio_packages():
    """Check installed GPIO packages"""
    print("\n🔍 Checking installed GPIO packages...")
    
    packages = [
        'RPi.GPIO',
        'Jetson.GPIO', 
        'adafruit-blinka',
        'adafruit-circuitpython-neopixel',
        'rpi-ws281x',
        'flask',
        'flask-cors'
    ]
    
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")
        except Exception as e:
            print(f"⚠️  {package} - error: {e}")

def test_gpio_import():
    """Test GPIO imports"""
    print("\n🧪 Testing GPIO imports...")
    
    # Test board import
    try:
        import board
        print("✅ board - OK")
    except Exception as e:
        print(f"❌ board - {e}")
    
    # Test neopixel import
    try:
        import neopixel
        print("✅ neopixel - OK")
    except Exception as e:
        print(f"❌ neopixel - {e}")
    
    # Test rpi_ws281x import
    try:
        from rpi_ws281x import PixelStrip
        print("✅ rpi_ws281x - OK")
    except Exception as e:
        print(f"❌ rpi_ws281x - {e}")

def suggest_fix():
    """Suggest fix based on findings"""
    print("\n💡 Suggested fixes:")
    print("1. Run the GPIO fix script:")
    print("   chmod +x fix_pi_gpio.sh")
    print("   ./fix_pi_gpio.sh")
    print("")
    print("2. Or manually fix:")
    print("   pip uninstall -y Jetson.GPIO RPi.GPIO adafruit-blinka")
    print("   pip install RPi.GPIO adafruit-blinka rpi-ws281x flask flask-cors")
    print("")
    print("3. If still having issues, try simulation mode:")
    print("   python3 run_simulation.py")

def main():
    print("🔧 LightBox GPIO Diagnostic Tool")
    print("=" * 40)
    
    is_pi = check_platform()
    check_gpio_packages()
    
    if is_pi:
        test_gpio_import()
    
    suggest_fix()

if __name__ == "__main__":
    main() 