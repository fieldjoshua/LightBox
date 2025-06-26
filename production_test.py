#!/usr/bin/env python3
"""
Production Hardware Test - Verify LED matrix works with color range fixes
Run with: sudo python3 production_test.py
"""

import time
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from Conductor import LEDMatrix

def test_color_ranges():
    """Test extreme color values to ensure no range errors"""
    print("🧪 Testing color range validation...")
    
    config = Config()
    matrix = LEDMatrix(config)
    
    # Test cases that might cause range errors
    test_cases = [
        ("Normal colors", [(128, 128, 128)] * 100),
        ("Max colors", [(255, 255, 255)] * 100),
        ("Min colors", [(0, 0, 0)] * 100),
        ("Extreme high", [(300, 300, 300)] * 100),  # Should be clamped
        ("Extreme low", [(-50, -50, -50)] * 100),   # Should be clamped
        ("Mixed extreme", [(500, -100, 128)] * 100), # Should be clamped
    ]
    
    all_passed = True
    
    for test_name, test_pixels in test_cases:
        print(f"   Testing {test_name}...")
        try:
            # Set the test pixels
            for i, (r, g, b) in enumerate(test_pixels):
                if i < len(matrix.pixels):
                    matrix.pixels[i] = (r, g, b)
            
            # Try to show (this is where range errors typically occur)
            matrix.clamp_pixels()
            if hasattr(matrix.pixels, 'show'):
                matrix.pixels.show()
                
            print(f"   ✅ {test_name} passed")
            
        except Exception as e:
            print(f"   ❌ {test_name} failed: {e}")
            all_passed = False
        
        time.sleep(0.1)  # Brief pause between tests
    
    return all_passed

def test_animations():
    """Test problematic animations with hardware"""
    print("🎨 Testing animations with hardware...")
    
    config = Config()
    matrix = LEDMatrix(config)
    
    # Test the previously problematic animations
    test_animations = ["hypnotic_cosmos", "aurora", "clouds"]
    
    all_passed = True
    
    for anim_name in test_animations:
        print(f"   Testing {anim_name}...")
        try:
            # Load the animation
            matrix.load_program(anim_name)
            
            # Run a few frames
            for frame in range(10):
                if matrix.current_program and hasattr(matrix.current_program, 'animate'):
                    matrix.current_program.animate(matrix.pixels, config, frame)
                    matrix.clamp_pixels()
                    
                    if hasattr(matrix.pixels, 'show'):
                        matrix.pixels.show()
                
                time.sleep(0.05)  # 20fps
            
            print(f"   ✅ {anim_name} completed successfully")
            
        except Exception as e:
            print(f"   ❌ {anim_name} failed: {e}")
            all_passed = False
    
    return all_passed

def check_sudo():
    """Check if running with sudo privileges"""
    if os.geteuid() != 0:
        print("❌ This test requires sudo privileges for hardware access")
        print("   Run with: sudo python3 production_test.py")
        return False
    return True

def main():
    """Run production hardware tests"""
    print("🔧 LightBox Production Hardware Test")
    print("=" * 50)
    
    if not check_sudo():
        sys.exit(1)
    
    # Test 1: Color range validation
    print("\n1️⃣ Color Range Validation Test")
    color_test_passed = test_color_ranges()
    
    # Test 2: Animation hardware test
    print("\n2️⃣ Animation Hardware Test")
    animation_test_passed = test_animations()
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 30)
    
    if color_test_passed and animation_test_passed:
        print("✅ All tests passed! Hardware is ready for production.")
        print("🌟 You can now run the full system with:")
        print("   sudo python3 CosmicLED.py")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above.")
        if not color_test_passed:
            print("   - Color range validation needs attention")
        if not animation_test_passed:
            print("   - Animation hardware compatibility needs work")
        sys.exit(1)

if __name__ == "__main__":
    main()