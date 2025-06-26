# flake8: noqa
"""
Feathers Animation for CosmicLED
Creates organic, flowing feather-like patterns with soft edges and natural movement
"""

import math

def animate(pixels, config, frame):
    """
    Feathery organic patterns with flowing, soft movements
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Animation parameters
    time_scale = config.speed * 0.08
    pattern_scale = config.scale * 1.5
    time_offset = frame * time_scale
    
    # Feather characteristics
    feather_count = 3  # Number of feather spines
    feather_spread = 2.5  # How spread out the feathers are
    barbule_frequency = 4.0  # Frequency of feather barbules
    
    # Matrix center
    center_x = config.matrix_width / 2.0
    center_y = config.matrix_height / 2.0
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            # Distance from center
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx**2 + dy**2)
            angle = math.atan2(dy, dx)
            
            # Create multiple feather spines
            brightness = 0.0
            
            for feather_id in range(feather_count):
                # Each feather has a different angle and phase
                feather_angle = (feather_id * 2 * math.pi / feather_count) + time_offset * 0.3
                spine_angle = feather_angle
                
                # Rotate point relative to feather spine
                rotated_angle = angle - spine_angle
                
                # Create feather spine (central shaft)
                spine_alignment = math.cos(rotated_angle)
                if spine_alignment > 0:  # Only on one side of the spine
                    spine_strength = spine_alignment ** 2
                    
                    # Distance along spine
                    spine_distance = distance * spine_alignment
                    
                    # Perpendicular distance from spine
                    perp_distance = distance * math.sin(rotated_angle)
                    
                    # Feather barbule pattern (the fluffy parts)
                    barbule_wave = math.sin(spine_distance * barbule_frequency + time_offset * 2)
                    barbule_envelope = math.exp(-abs(perp_distance) * feather_spread)
                    
                    # Feather tip falloff
                    tip_falloff = math.exp(-spine_distance * 0.3)
                    
                    # Feather width variation along spine
                    width_variation = (math.sin(spine_distance * 2 + time_offset) * 0.3 + 0.7)
                    
                    # Combine feather elements
                    feather_intensity = (
                        spine_strength * 
                        barbule_envelope * 
                        tip_falloff * 
                        width_variation *
                        (barbule_wave * 0.5 + 0.8)  # Barbule texture
                    )
                    
                    # Add soft flowing motion
                    flow_offset = math.sin(x * 0.3 + y * 0.2 + time_offset * 1.5) * 0.2
                    feather_intensity *= (1.0 + flow_offset)
                    
                    brightness += feather_intensity * 0.6
            
            # Add subtle background texture
            background_texture = (
                math.sin(x * 0.5 + time_offset * 0.8) * 
                math.sin(y * 0.4 + time_offset * 0.6) * 0.1 + 0.1
            )
            brightness += background_texture
            
            # Normalize effect brightness (global brightness applied later)
            brightness = max(0.0, min(1.0, brightness))
            
            # Color based on position and time
            hue_base = (config.hue_offset + time_offset * 20) % 360
            hue_variation = (
                math.sin(x * 0.3 + time_offset * 0.5) * 30 +
                math.sin(y * 0.25 + time_offset * 0.3) * 20
            )
            pixel_hue = (hue_base + hue_variation) % 360
            
            # Get color
            if hasattr(config, 'get_palette_color'):
                palette_pos = (pixel_hue / 360.0) % 1.0
                r, g, b = config.get_palette_color(palette_pos)
                r = int(r * brightness)
                g = int(g * brightness)
                b = int(b * brightness)
            else:
                r, g, b = config.hsv_to_rgb(pixel_hue, config.saturation, brightness)
            
            # Apply gamma correction
            r = int(pow(r / 255.0, config.gamma) * 255)
            g = int(pow(g / 255.0, config.gamma) * 255)
            b = int(pow(b / 255.0, config.gamma) * 255)
            
            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Set pixel
            pixel_index = config.xy_to_index(x, y)
            try:
                if hasattr(pixels, '__setitem__'):
                    pixels[pixel_index] = (
                        int(max(0, min(255, r))),
                        int(max(0, min(255, g))),
                        int(max(0, min(255, b)))
                    )
                else:
                    pixels[pixel_index] = (
                        int(max(0, min(255, r))),
                        int(max(0, min(255, g))),
                        int(max(0, min(255, b)))
                    )
            except IndexError:
                pass

# Animation metadata
ANIMATION_INFO = {
    'name': 'Feathers',
    'description': 'Organic feather-like patterns with flowing barbules',
    'author': 'CosmicLED',
    'version': '1.0',
    'parameters': {
        'speed': 'Feather flow speed (0.1-5.0)',
        'scale': 'Feather size and spread (0.1-3.0)',
        'hue_offset': 'Color shift (0-360 degrees)',
        'saturation': 'Color saturation (0.0-1.0)'
    },
    'features': [
        'Multiple feather spines with natural angles',
        'Organic barbule patterns',
        'Soft edge falloff',
        'Flowing motion and color shifts',
        'Natural feather structure simulation'
    ]
}