#!/usr/bin/env python3
"""
CosmicLED Diagnostic Script
Run this to troubleshoot LED matrix issues
"""

import sys
import time
from pathlib import Path

def check_gpio_access():
    """Test GPIO/NeoPixel library access"""
    print("🔍 Checking GPIO access...")
    try:
        import board
        import neopixel
        print("✅ GPIO libraries imported successfully")
        return True
    except ImportError as e:
        print(f"❌ GPIO libraries not available: {e}")
        print("💡 Run: sudo apt install python3-dev python3-pip")
        print("💡 Then: pip install adafruit-circuitpython-neopixel")
        return False

def check_permissions():
    """Check if running with proper permissions"""
    print("🔍 Checking permissions...")
    import os
    if os.geteuid() == 0:
        print("✅ Running as root (required for GPIO)")
        return True
    else:
        print("❌ Not running as root")
        print("💡 Run with: sudo python3 diagnose.py")
        return False

def test_led_initialization():
    """Test LED strip initialization"""
    print("🔍 Testing LED initialization...")
    try:
        import board
        import neopixel
        
        # Try to initialize LED strip
        pixels = neopixel.NeoPixel(
            board.D12,  # GPIO 12
            100,        # 10x10 matrix
            brightness=0.3,
            auto_write=False,
            pixel_order=neopixel.GRB
        )
        print("✅ LED strip initialized successfully")
        return pixels
    except Exception as e:
        print(f"❌ LED initialization failed: {e}")
        print("💡 Check hardware connections:")
        print("   - LED data wire to GPIO12 (pin 32)")
        print("   - Use 3.3V to 5V level shifter")
        print("   - External 5V power supply for LEDs")
        print("   - Common ground between Pi and LED power")
        return None

def test_basic_animation(pixels):
    """Test basic LED animation"""
    print("🔍 Testing basic animation...")
    if not pixels:
        print("❌ Cannot test - no LED strip available")
        return False
        
    try:
        print("🎨 Running basic color test (5 seconds)...")
        
        # Test 1: All red
        pixels.fill((50, 0, 0))
        pixels.show()
        time.sleep(1)
        
        # Test 2: All green  
        pixels.fill((0, 50, 0))
        pixels.show()
        time.sleep(1)
        
        # Test 3: All blue
        pixels.fill((0, 0, 50))
        pixels.show()
        time.sleep(1)
        
        # Test 4: All white
        pixels.fill((30, 30, 30))
        pixels.show()
        time.sleep(1)
        
        # Test 5: Turn off
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(1)
        
        print("✅ Basic animation test completed")
        return True
        
    except Exception as e:
        print(f"❌ Animation test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    try:
        from config import Config
        config = Config()
        print(f"✅ Config loaded: {config.matrix_width}x{config.matrix_height}, FPS: {config.fps}")
        return config
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return None

def test_program_loading():
    """Test animation program loading"""
    print("🔍 Testing program loading...")
    try:
        # Test matrix_test program
        test_path = Path("scripts/matrix_test.py")
        if test_path.exists():
            print("✅ Found matrix_test.py")
            
            # Try to import it
            import importlib.util
            spec = importlib.util.spec_from_file_location("matrix_test", test_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'animate'):
                print("✅ matrix_test.py has animate function")
                return True
            else:
                print("❌ matrix_test.py missing animate function")
                return False
        else:
            print("❌ matrix_test.py not found in scripts/")
            return False
            
    except Exception as e:
        print(f"❌ Program loading failed: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🌟 CosmicLED Diagnostic Tool")
    print("=" * 40)
    
    # Check basic requirements
    gpio_ok = check_gpio_access()
    perms_ok = check_permissions()
    
    if not gpio_ok or not perms_ok:
        print("\n❌ Basic requirements not met. Fix these issues first.")
        return False
    
    # Test configuration
    config = test_config_loading()
    
    # Test LED hardware
    pixels = test_led_initialization()
    
    # Test basic animation
    if pixels:
        animation_ok = test_basic_animation(pixels)
        
        # Clean up
        pixels.fill((0, 0, 0))
        pixels.show()
    else:
        animation_ok = False
    
    # Test program loading
    program_ok = test_program_loading()
    
    print("\n" + "=" * 40)
    print("📊 DIAGNOSTIC SUMMARY:")
    print(f"  GPIO Access: {'✅' if gpio_ok else '❌'}")
    print(f"  Permissions: {'✅' if perms_ok else '❌'}")
    print(f"  Configuration: {'✅' if config else '❌'}")
    print(f"  LED Hardware: {'✅' if pixels else '❌'}")
    print(f"  Basic Animation: {'✅' if animation_ok else '❌'}")
    print(f"  Program Loading: {'✅' if program_ok else '❌'}")
    
    if all([gpio_ok, perms_ok, config, pixels, animation_ok, program_ok]):
        print("\n🎉 All tests passed! Your system should work.")
        print("💡 Try running: sudo python3 CosmicLED.py")
    else:
        print("\n⚠️  Some tests failed. Fix the issues above.")
    
    return True

if __name__ == "__main__":
    main()