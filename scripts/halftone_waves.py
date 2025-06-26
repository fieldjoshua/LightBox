#!/usr/bin/env python3
"""
Halftone Waves Animation
Recreates a halftone wave effect with concentric circles pulsing from center
Based on the JavaScript canvas animation pattern
"""

import math

ANIMATION_INFO = {
    'name': 'Halftone Waves',
    'description': 'Concentric wave pattern with halftone circle effects',
    'version': '1.0',
    'author': 'Claude Code',
    'parameters': {
        'speed': 'Wave propagation speed (0.1-2.0)',
        'scale': 'Wave frequency/density (0.5-3.0)',
        'brightness': 'Overall brightness (0.1-1.0)'
    },
    'features': [
        'Halftone dot pattern',
        'Concentric wave propagation',
        'Distance-based sizing',
        'Smooth fading trails'
    ]
}

def animate(pixels, config, frame):
    """
    Halftone wave animation
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Clear with slight fade for trail effect
    for i in range(len(pixels)):
        # Get existing color and fade it
        try:
            existing_r, existing_g, existing_b = pixels[i]
            # Fade to black (trail effect)
            fade_factor = 0.85
            pixels[i] = (
                int(existing_r * fade_factor),
                int(existing_g * fade_factor),
                int(existing_b * fade_factor)
            )
        except:
            pixels[i] = (0, 0, 0)
    
    # Animation timing
    time_factor = frame * config.speed * 0.05
    
    # Matrix center
    center_x = config.matrix_width / 2
    center_y = config.matrix_height / 2
    
    # Maximum distance from center
    max_distance = math.sqrt(
        (config.matrix_width / 2) ** 2 + 
        (config.matrix_height / 2) ** 2
    )
    
    # Grid-based halftone pattern
    grid_size = max(1, int(4 / config.scale))  # Adjustable grid density
    
    for y in range(0, config.matrix_height, grid_size):
        for x in range(0, config.matrix_width, grid_size):
            # Distance from center
            distance_from_center = math.sqrt(
                (x - center_x) ** 2 + 
                (y - center_y) ** 2
            )
            
            # Normalize distance (0 to 1)
            normalized_distance = distance_from_center / max_distance
            
            # Wave calculation
            wave_offset = math.sin(normalized_distance * 10 * config.scale - time_factor) * 0.5 + 0.5
            
            # Calculate circle size based on wave
            circle_size = int(grid_size * wave_offset * 0.8)
            
            # Draw circle pattern
            for dy in range(-circle_size, circle_size + 1):
                for dx in range(-circle_size, circle_size + 1):
                    px = x + dx
                    py = y + dy
                    
                    # Check if pixel is within matrix bounds
                    if 0 <= px < config.matrix_width and 0 <= py < config.matrix_height:
                        # Distance from circle center
                        circle_dist = math.sqrt(dx**2 + dy**2)
                        
                        # Only draw if within circle radius
                        if circle_dist <= circle_size / 2:
                            index = config.xy_to_index(px, py)
                            if 0 <= index < len(pixels):
                                # Smooth circle edge with anti-aliasing
                                edge_smooth = max(0, min(1, 1 - (circle_dist - circle_size/2 + 1)))
                                
                                # Color intensity based on wave and position
                                intensity = wave_offset * edge_smooth * config.brightness
                                
                                # Color based on distance and time for variety
                                hue_shift = (normalized_distance * 2 + time_factor * 0.1) % 1.0
                                
                                if hue_shift < 0.33:
                                    # Red to Yellow
                                    r = int(255 * intensity)
                                    g = int(255 * intensity * (hue_shift * 3))
                                    b = 0
                                elif hue_shift < 0.66:
                                    # Yellow to Cyan
                                    hue_local = (hue_shift - 0.33) * 3
                                    r = int(255 * intensity * (1 - hue_local))
                                    g = int(255 * intensity)
                                    b = int(255 * intensity * hue_local)  
                                else:
                                    # Cyan to Red
                                    hue_local = (hue_shift - 0.66) * 3
                                    r = int(255 * intensity * hue_local)
                                    g = int(255 * intensity * (1 - hue_local))
                                    b = int(255 * intensity * (1 - hue_local))
                                
                                # Ensure valid color values
                                r = max(0, min(255, r))
                                g = max(0, min(255, g))
                                b = max(0, min(255, b))
                                
                                # Apply color correction
                                if hasattr(config, 'correct_color'):
                                    r, g, b = config.correct_color(r, g, b)
                                
                                # Blend with existing color (additive for wave effects)
                                existing_r, existing_g, existing_b = pixels[index]
                                final_r = min(255, existing_r + r)
                                final_g = min(255, existing_g + g)
                                final_b = min(255, existing_b + b)
                                
                                pixels[index] = (final_r, final_g, final_b)