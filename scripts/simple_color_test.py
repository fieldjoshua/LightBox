#!/usr/bin/env python3
"""
Simple Color Test - Very basic, stable color testing
"""

ANIMATION_INFO = {
    'name': 'Simple Color Test',
    'description': 'Basic color order test',
    'version': '1.0',
    'author': 'Claude Code'
}

def animate(pixels, config, frame):
    """Very simple color test"""
    # Clear first
    for i in range(len(pixels)):
        pixels[i] = (0, 0, 0)
    
    # Simple test: alternate between red and green every 3 seconds
    # At 15fps, 45 frames = 3 seconds
    test_time = (frame // 45) % 4
    
    if test_time == 0:
        # Pure red
        color = (255, 0, 0)
    elif test_time == 1:
        # Pure green  
        color = (0, 255, 0)
    elif test_time == 2:
        # GRB test - send green to try to get red
        color = (0, 255, 0)
    else:
        # Off
        color = (0, 0, 0)
    
    # Light up center pixel only
    center_index = config.xy_to_index(config.matrix_width // 2, config.matrix_height // 2)
    if 0 <= center_index < len(pixels):
        pixels[center_index] = color