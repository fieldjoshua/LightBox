#!/usr/bin/env python3
"""
Simple test to replicate the exact Conductor logic
"""
import time
import board
import neopixel

def test_exact_logic():
    """Test with exact same logic as Conductor"""
    print("🔧 Testing exact Conductor logic...")
    
    # Initialize exactly like Conductor
    matrix_width = 10
    matrix_height = 10
    brightness = 0.3
    
    pixels = neopixel.NeoPixel(
        board.D12,  # GPIO 12
        matrix_width * matrix_height,
        brightness=brightness,
        auto_write=False,
        pixel_order=neopixel.GRB,
    )
    print(f"✅ LED matrix initialized: {matrix_width}x{matrix_height}")
    
    # Test basic setting and show
    print("🎯 Setting test pattern...")
    pixels[0] = (255, 0, 0)  # Red
    pixels[1] = (0, 255, 0)  # Green  
    pixels[2] = (0, 0, 255)  # Blue
    pixels.show()
    print("✅ Test pattern set - should see Red, Green, Blue")
    
    time.sleep(3)
    
    # Clear
    pixels.fill((0, 0, 0))
    pixels.show()
    print("✅ Cleared")
    
    return pixels

def test_animation_loop():
    """Test animation loop logic"""
    print("🎨 Testing animation loop...")
    
    pixels = test_exact_logic()
    
    # Animation loop (simplified cosmic)
    frame_count = 0
    while frame_count < 100:  # Short test
        start_time = time.time()
        
        # Simple animation - cycle through colors
        for i in range(10):  # First 10 pixels
            hue = (frame_count + i * 10) % 360
            if hue < 120:
                r, g, b = 255, 0, 0  # Red
            elif hue < 240:
                r, g, b = 0, 255, 0  # Green
            else:
                r, g, b = 0, 0, 255  # Blue
            
            # Apply brightness
            r = int(r * 0.3)
            g = int(g * 0.3)
            b = int(b * 0.3)
            
            pixels[i] = (r, g, b)
        
        # Show pixels
        pixels.show()
        
        # Debug every 30 frames
        if frame_count % 30 == 0:
            print(f"🌟 Frame {frame_count}: Animation running, pixels shown")
        
        frame_count += 1
        
        # Control frame rate
        elapsed = time.time() - start_time
        sleep_time = max(0, (1.0 / 30) - elapsed)  # 30 FPS
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    # Clear
    pixels.fill((0, 0, 0))
    pixels.show()
    print("✅ Animation test complete")

if __name__ == "__main__":
    test_animation_loop() 