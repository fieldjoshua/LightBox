#!/usr/bin/env python3
"""
Simple Hypercube Test - Debug version to test loading
"""

import math
import colorsys

ANIMATION_INFO = {
    'name': 'Hypercube Simple Test',
    'description': 'Simplified hypercube test for debugging',
    'version': '1.0',
    'author': 'Claude Code',
    'parameters': {
        'speed': 'Rotation speed (0.1-2.0)',
        'scale': 'Size (0.5-2.0)'
    },
    'features': ['Debug test', 'Simple rotation']
}

def animate(pixels, config, frame):
    """Simplified animation for testing"""
    # Clear display
    for i in range(len(pixels)):
        pixels[i] = (0, 0, 0)
    
    # Simple rotating square test
    center_x = config.matrix_width / 2
    center_y = config.matrix_height / 2
    
    # 120 BPM timing
    beat_time = (frame / config.fps) / 0.5  # 0.5 seconds per beat
    beat_phase = beat_time % 1.0
    
    # Beat pulse
    pulse_intensity = 1.0 if beat_phase < 0.2 else 0.5
    
    # Draw a simple square that rotates
    angle = frame * config.speed * 0.05
    size = config.scale * 2 * pulse_intensity
    
    # Square corners
    corners = [
        (-size, -size), (size, -size), 
        (size, size), (-size, size)
    ]
    
    # Rotate corners
    rotated_corners = []
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    for x, y in corners:
        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a
        rotated_corners.append((rx + center_x, ry + center_y))
    
    # Color based on beat
    beat_color_phase = int(beat_time / 8) % 4  # 8 beats per color
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    color = colors[beat_color_phase]
    
    # Draw the square
    for i in range(4):
        x1, y1 = rotated_corners[i]
        x2, y2 = rotated_corners[(i + 1) % 4]
        
        # Simple line drawing
        steps = int(max(abs(x2 - x1), abs(y2 - y1), 1))
        for step in range(steps + 1):
            t = step / steps if steps > 0 else 0
            px = int(x1 + t * (x2 - x1))
            py = int(y1 + t * (y2 - y1))
            
            if 0 <= px < config.matrix_width and 0 <= py < config.matrix_height:
                index = config.xy_to_index(px, py)
                if 0 <= index < len(pixels):
                    r, g, b = color
                    r = int(r * config.brightness * pulse_intensity)
                    g = int(g * config.brightness * pulse_intensity)
                    b = int(b * config.brightness * pulse_intensity)
                    
                    # Apply color correction
                    if hasattr(config, 'correct_color'):
                        r, g, b = config.correct_color(r, g, b)
                    
                    pixels[index] = (r, g, b)
    
    # Center beat pulse
    if beat_phase < 0.2:
        cx, cy = int(center_x), int(center_y)
        if 0 <= cx < config.matrix_width and 0 <= cy < config.matrix_height:
            index = config.xy_to_index(cx, cy)
            if 0 <= index < len(pixels):
                # Apply color correction to white center pulse
                r, g, b = (255, 255, 255)
                if hasattr(config, 'correct_color'):
                    r, g, b = config.correct_color(r, g, b)
                pixels[index] = (r, g, b)