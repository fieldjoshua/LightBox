#!/usr/bin/env python3
from rpi_ws281x import PixelStrip, Color
import time

def test_pin(pin):
    try:
        print(f"Testing GPIO{pin}...")
        strip = PixelStrip(100, pin)
        strip.begin()
        
        # Test red
        strip.setPixelColor(0, Color(255, 0, 0))
        strip.show()
        print(f"GPIO{pin}: First pixel RED - check LED")
        time.sleep(1)
        
        # Test green  
        strip.setPixelColor(0, Color(0, 255, 0))
        strip.show()
        print(f"GPIO{pin}: First pixel GREEN - check LED")
        time.sleep(1)
        
        # Test blue
        strip.setPixelColor(0, Color(0, 0, 255))
        strip.show() 
        print(f"GPIO{pin}: First pixel BLUE - check LED")
        time.sleep(1)
        
        # Off
        strip.setPixelColor(0, Color(0, 0, 0))
        strip.show()
        print(f"GPIO{pin}: OFF")
        time.sleep(0.5)
        
        return True
    except Exception as e:
        print(f"GPIO{pin}: ERROR - {e}")
        return False

if __name__ == "__main__":
    pins_to_test = [10, 12, 18, 21]
    
    for pin in pins_to_test:
        success = test_pin(pin)
        if not success:
            continue
        
        response = input(f"Did you see any LED activity on GPIO{pin}? (y/n): ")
        if response.lower().startswith('y'):
            print(f"SUCCESS: LEDs are connected to GPIO{pin}")
            break
    else:
        print("No LED activity detected on any tested pins")
        print("Check LED power supply and wiring")