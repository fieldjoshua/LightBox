#!/usr/bin/env python3
"""
Color Order Test - Display pure colors to determine correct order
"""

ANIMATION_INFO = {
    'name': 'Color Order Test',
    'description': 'Test different color orders to find the correct one',
    'version': '1.0',
    'author': 'Claude Code'
}

def animate(pixels, config, frame):
    """Test color orders - each test lasts 5 seconds"""
    # Clear display
    for i in range(len(pixels)):
        pixels[i] = (0, 0, 0)
    
    # Each phase lasts 5 seconds (75 frames at 15fps), no repeat
    test_phase = frame // 75
    
    if test_phase == 0:
        # Test 1: Pure red (255, 0, 0)
        color = (255, 0, 0)
        label = "TEST 1: Pure RED (255,0,0)"
    elif test_phase == 1:
        # Test 2: Pure green (0, 255, 0)
        color = (0, 255, 0)
        label = "TEST 2: Pure GREEN (0,255,0)"
    elif test_phase == 2:
        # Test 3: Pure blue (0, 0, 255)
        color = (0, 0, 255)
        label = "TEST 3: Pure BLUE (0,0,255)"
    elif test_phase == 3:
        # Test 4: GRB correction - send green to get red
        color = (0, 255, 0)  
        label = "TEST 4: GRB Test - should show RED"
    elif test_phase == 4:
        # Test 5: RGB standard
        color = (255, 0, 0)
        label = "TEST 5: RGB Test - should show RED"
    elif test_phase == 5:
        # Test 6: White
        color = (255, 255, 255)
        label = "TEST 6: WHITE"
    else:
        # Done - turn off
        color = (0, 0, 0)
        label = "TESTS COMPLETE"
    
    # Fill entire matrix for better visibility
    for i in range(len(pixels)):
        if test_phase <= 5:
            r, g, b = color
            # Use full brightness for testing
            r = r  # Full brightness, no dimming
            g = g
            b = b
            pixels[i] = (r, g, b)
        else:
            pixels[i] = (0, 0, 0)
    
    # Print current test every 75 frames (start of each test)
    if frame % 75 == 0 and test_phase <= 6:
        print(f"\\n=== {label} ===")
        print(f"Frame {frame}: RGB values sent to LEDs: ({color[0]}, {color[1]}, {color[2]})")
        if test_phase < 6:
            print(f"This test runs for 5 seconds...")