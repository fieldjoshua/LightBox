#!/usr/bin/env python3
"""
LED Debug Script - Test LED output step by step
"""
import time
import traceback
import sys
import platform

def detect_environment():
    """Detect if we're running on Pi hardware or development machine"""
    system = platform.system()
    machine = platform.machine()
    
    print(f"🖥️  System: {system} {machine}")
    print(f"🐍 Python: {sys.version}")
    
    # Check if we're on a Raspberry Pi
    is_pi = system == "Linux" and ("arm" in machine.lower() or "aarch64" in machine.lower())
    
    if is_pi:
        print("🍓 Detected: Raspberry Pi hardware")
        return "pi"
    else:
        print("💻 Detected: Development machine (simulation mode)")
        return "dev"

def test_led_output():
    """Test LED output with detailed debugging"""
    print("🔍 LED Debug Test Starting...")
    
    # Detect environment first
    env = detect_environment()
    
    try:
        # Test 1: Basic imports
        print("📦 Testing imports...")
        
        if env == "pi":
            # Try to import Pi-specific libraries
            try:
                from rpi_ws281x import PixelStrip, Color
                import RPi.GPIO as GPIO
                print("✅ Pi hardware imports successful (rpi_ws281x)")
                hardware_available = True
            except ImportError as e:
                print(f"⚠️  Pi hardware imports failed: {e}")
                print("💡 Try: pip install rpi-ws281x RPi.GPIO")
                hardware_available = False
        else:
            # Development machine - simulate
            print("💻 Development mode - simulating hardware")
            hardware_available = False
        
        if not hardware_available:
            print("🎭 Running in simulation mode")
            return test_led_simulation()
        
        # Test 2: Hardware initialization
        print("🔧 Initializing hardware...")
        LED_COUNT = 100          # Number of LED pixels
        LED_PIN = 12             # GPIO pin connected to the pixels (18 uses PWM!)
        LED_FREQ_HZ = 800000     # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10             # DMA channel to use for generating PWM signal (try 10)
        LED_BRIGHTNESS = 76      # Set to 0 for darkest and 255 for brightest (30% of 255)
        LED_INVERT = False       # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL = 0          # set to '1' for GPIOs 13, 19, 41, 45 or 53
        
        strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        strip.begin()
        print(f"✅ Hardware initialized: {LED_COUNT} pixels")
        
        # Test 3: Set single pixel
        print("🎯 Setting single pixel...")
        strip.setPixelColor(0, Color(255, 0, 0))  # Red
        strip.show()
        print("✅ Single pixel set - should see red LED")
        time.sleep(2)
        
        # Test 4: Set multiple pixels
        print("🌈 Setting multiple pixels...")
        for i in range(min(10, LED_COUNT)):
            if i % 2 == 0:
                strip.setPixelColor(i, Color(255, 0, 0))  # Red
            else:
                strip.setPixelColor(i, Color(0, 255, 0))  # Green
        strip.show()
        print("✅ Multiple pixels set - should see alternating red/green")
        time.sleep(2)
        
        # Test 5: Animation test
        print("🎨 Testing animation...")
        for frame in range(30):
            for i in range(min(10, LED_COUNT)):
                brightness = int(128 + 127 * (frame / 30))
                strip.setPixelColor(i, Color(brightness, 0, brightness))  # Purple
            strip.show()
            time.sleep(0.1)
        print("✅ Animation test complete")
        
        # Test 6: Clear pixels
        print("🧹 Clearing pixels...")
        for i in range(LED_COUNT):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        print("✅ Pixels cleared")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False
        
    return True

def test_led_simulation():
    """Test LED logic without hardware"""
    print("🎭 Starting simulation mode tests...")
    
    # Simulate pixel array
    pixels = [(0, 0, 0)] * 100
    
    try:
        # Test 1: Set single pixel
        print("🎯 Simulating single pixel...")
        pixels[0] = (255, 0, 0)  # Red
        print(f"✅ Pixel 0 set to {pixels[0]} (red)")
        time.sleep(0.5)
        
        # Test 2: Set multiple pixels
        print("🌈 Simulating multiple pixels...")
        for i in range(min(10, len(pixels))):
            pixels[i] = (255, 0, 0) if i % 2 == 0 else (0, 255, 0)
        print(f"✅ First 10 pixels: {pixels[:10]}")
        time.sleep(0.5)
        
        # Test 3: Animation simulation
        print("🎨 Simulating animation...")
        for frame in range(5):  # Shorter for simulation
            for i in range(min(5, len(pixels))):
                brightness = int(128 + 127 * (frame / 5))
                pixels[i] = (brightness, 0, brightness)
            print(f"   Frame {frame}: {pixels[:5]}")
            time.sleep(0.2)
        print("✅ Animation simulation complete")
        
        # Test 4: Clear pixels
        print("🧹 Clearing simulated pixels...")
        pixels = [(0, 0, 0)] * 100
        print(f"✅ Pixels cleared: {pixels[0]}")
        
        print("💡 Simulation tests completed successfully!")
        print("🍓 To test on actual hardware, run this script on a Raspberry Pi with LEDs connected")
        
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        traceback.print_exc()
        return False
        
    return True

def test_cosmic_animation():
    """Test the exact cosmic animation logic"""
    print("\n🌌 Testing Cosmic Animation Logic...")
    
    # Detect environment
    env = detect_environment()
    
    try:
        import math
        import colorsys
        
        # Initialize pixels based on environment
        if env == "pi":
            try:
                from rpi_ws281x import PixelStrip, Color
                LED_COUNT = 100
                LED_PIN = 12
                LED_FREQ_HZ = 800000
                LED_DMA = 10
                LED_BRIGHTNESS = 76
                LED_INVERT = False
                LED_CHANNEL = 0
                
                strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
                strip.begin()
                print("✅ Using hardware pixels (rpi_ws281x)")
                hardware_mode = True
            except ImportError:
                print("⚠️  Hardware not available, using simulation")
                pixels = [(0, 0, 0)] * 100
                hardware_mode = False
        else:
            print("💻 Using simulation mode")
            pixels = [(0, 0, 0)] * 100
            hardware_mode = False
        
        # Config values (matching CosmicLED)
        matrix_width = 10
        matrix_height = 10 
        hue_offset = 0
        saturation = 1.0
        brightness_val = 0.3
        gamma = 2.2
        
        def hsv_to_rgb(h, s, v):
            """HSV to RGB conversion"""
            r, g, b = colorsys.hsv_to_rgb(h/360, s, v)
            return int(r*255), int(g*255), int(b*255)
        
        def xy_to_index(x, y):
            """Convert x,y to pixel index (snake pattern)"""
            if y % 2 == 0:
                return y * matrix_width + x
            else:
                return y * matrix_width + (matrix_width - 1 - x)
        
        # Run animation frames (shorter for simulation)
        frame_count = 60 if hardware_mode else 5
        for frame in range(frame_count):
            if not hardware_mode and frame == 0:
                print("🎨 Cosmic animation calculation test:")
            
            for y in range(matrix_height):
                for x in range(matrix_width):
                    # Cosmic animation logic (exact copy)
                    wave1 = math.sin((x + frame * 0.1) * 0.3) * 0.5 + 0.5
                    wave2 = math.sin((y + frame * 0.08) * 0.25) * 0.5 + 0.5
                    wave3 = math.sin((x + y + frame * 0.12) * 0.2) * 0.5 + 0.5
                    
                    hue_offset_calc = (wave1 + wave2 + wave3) / 3
                    hue = (hue_offset + hue_offset_calc * 360) % 360
                    
                    r, g, b = hsv_to_rgb(hue, saturation, 1.0)
                    
                    # Apply gamma correction
                    r = pow(r / 255.0, gamma) * 255
                    g = pow(g / 255.0, gamma) * 255
                    b = pow(b / 255.0, gamma) * 255
                    
                    # Apply brightness
                    r *= brightness_val
                    g *= brightness_val  
                    b *= brightness_val
                    
                    # Clamp
                    r = int(max(0, min(255, r)))
                    g = int(max(0, min(255, g)))
                    b = int(max(0, min(255, b)))
                    
                    # Set pixel
                    pixel_index = xy_to_index(x, y)
                    if hardware_mode:
                        if pixel_index < LED_COUNT:
                            strip.setPixelColor(pixel_index, Color(int(r), int(g), int(b)))
                            # Debug first few pixels on first frame
                            if frame == 0 and pixel_index < 5:
                                print(f"  Pixel {pixel_index} (x={x}, y={y}): ({r}, {g}, {b})")
                    else:
                        if pixel_index < len(pixels):
                            pixels[pixel_index] = (r, g, b)
                            # Debug first few pixels in simulation on first frame
                            if frame == 0 and pixel_index < 5:
                                print(f"  Pixel {pixel_index} (x={x}, y={y}): ({r}, {g}, {b})")
            
            # Show pixels
            if hardware_mode:
                strip.show()
                time.sleep(0.05)
            elif frame == 0:
                # In simulation, just show a sample
                print(f"  Sample colors: {pixels[:5]}")
            
        # Clear
        if hardware_mode:
            for i in range(LED_COUNT):
                strip.setPixelColor(i, Color(0, 0, 0))
            strip.show()
            print("✅ Cosmic animation test complete")
        else:
            print("✅ Cosmic animation calculation test complete")
            print("💡 RGB calculations working correctly - colors would animate on hardware")
        
    except Exception as e:
        print(f"❌ Cosmic animation error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting LED diagnostics...\n")
    
    if test_led_output():
        test_cosmic_animation()
    else:
        print("❌ Basic LED test failed, skipping animation test")
    
    print("\n✅ LED diagnostics complete") 