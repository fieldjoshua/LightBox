#!/usr/bin/env python3
import board
import neopixel
import time

print("🔧 Simple LED Test - Force LEDs ON")

# Initialize NeoPixel on GPIO12
pixels = neopixel.NeoPixel(board.D12, 100, brightness=0.3, auto_write=False)

try:
    # Test 1: All red for 3 seconds
    print("Setting ALL pixels RED...")
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(3)
    
    # Test 2: All green for 3 seconds  
    print("Setting ALL pixels GREEN...")
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(3)
    
    # Test 3: First 10 pixels bright white
    print("Setting first 10 pixels WHITE...")
    pixels.fill((0, 0, 0))  # Clear all
    for i in range(10):
        pixels[i] = (255, 255, 255)
    pixels.show()
    time.sleep(3)
    
    # Test 4: Keep last state for observation
    print("LEDs should stay WHITE - press Ctrl+C to exit")
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nTurning off LEDs...")
    pixels.fill((0, 0, 0))
    pixels.show()
    print("Test complete")