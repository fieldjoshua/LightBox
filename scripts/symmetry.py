"""
Symmetry Animation for CosmicLED
Creates symmetrical patterns radiating from the center of the matrix
"""

import math

def animate(pixels, config, frame):
    """
    Symmetrical pattern animation with radial and mirror symmetries
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Animation parameters
    rotation_speed = config.speed * 0.1
    pattern_scale = config.scale * 2.0
    time_offset = frame * rotation_speed
    
    # Matrix center point
    center_x = config.matrix_width / 2.0
    center_y = config.matrix_height / 2.0
    
    # Maximum distance from center (for normalization)
    max_distance = math.sqrt(center_x**2 + center_y**2)
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            # Calculate distance and angle from center
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx**2 + dy**2)
            angle = math.atan2(dy, dx)
            
            # Normalize distance
            norm_distance = distance / max_distance if max_distance > 0 else 0
            
            # Create symmetrical patterns
            
            # Radial pattern (symmetric around center)
            radial_pattern = math.sin(distance * pattern_scale * 0.3 + time_offset)
            
            # Angular pattern (rotational symmetry)
            # Use 8-fold symmetry (octagon)
            symmetry_order = 8
            angular_pattern = math.cos(angle * symmetry_order + time_offset * 2)
            
            # Mirror symmetry patterns
            mirror_x = math.sin(abs(dx) * pattern_scale * 0.2 + time_offset * 0.7)
            mirror_y = math.sin(abs(dy) * pattern_scale * 0.2 + time_offset * 0.5)
            
            # Diamond pattern (based on Manhattan distance)
            manhattan_distance = abs(dx) + abs(dy)
            diamond_pattern = math.cos(manhattan_distance * pattern_scale * 0.15 + time_offset * 1.2)
            
            # Combine all symmetrical patterns
            combined_pattern = (
                radial_pattern * 0.3 +
                angular_pattern * 0.3 +
                mirror_x * 0.2 +
                mirror_y * 0.2 +
                diamond_pattern * 0.2
            )
            
            # Normalize to 0-1 range
            brightness = (combined_pattern + 1.0) / 2.0
            
            # Add pulsing effect
            pulse = math.sin(time_offset * 3) * 0.2 + 0.8
            brightness *= pulse
            
            # Distance-based attenuation (brighter in center)
            center_bias = 1.0 - (norm_distance * 0.3)
            brightness *= center_bias
            
            # Apply brightness scaling
            brightness *= config.brightness_scale
            brightness = max(0.0, min(1.0, brightness))
            
            # Color calculation
            # Use angle and distance for hue variation
            hue_from_angle = (math.degrees(angle) + 180) % 360
            hue_from_distance = norm_distance * 120  # 0-120 degree range
            
            # Combine hue sources
            pixel_hue = (
                config.hue_offset + 
                hue_from_angle * 0.5 + 
                hue_from_distance * 0.3 +
                time_offset * 10
            ) % 360
            
            # Get color from palette or HSV
            if hasattr(config, 'get_palette_color'):
                # Use palette color
                palette_pos = (pixel_hue / 360.0) % 1.0
                r, g, b = config.get_palette_color(palette_pos)
                
                # Apply brightness
                r = int(r * brightness)
                g = int(g * brightness)
                b = int(b * brightness)
            else:
                # Fallback to HSV conversion
                r, g, b = config.hsv_to_rgb(
                    pixel_hue, 
                    config.saturation, 
                    brightness
                )
            
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
                    pixels[pixel_index] = (r, g, b)
                else:
                    pixels[pixel_index] = (r, g, b)
            except IndexError:
                # Handle matrix size mismatches gracefully
                pass

# Animation metadata
ANIMATION_INFO = {
    'name': 'Symmetry',
    'description': 'Symmetrical patterns with radial and mirror effects',
    'author': 'CosmicLED',
    'version': '1.0',
    'parameters': {
        'speed': 'Rotation speed (0.1-5.0)',
        'scale': 'Pattern scale (0.1-3.0)', 
        'brightness_scale': 'Overall brightness (0.0-2.0)',
        'hue_offset': 'Color shift (0-360 degrees)',
        'saturation': 'Color saturation (0.0-1.0)'
    },
    'features': [
        '8-fold rotational symmetry',
        'Radial patterns from center',
        'Mirror symmetry effects',
        'Diamond/Manhattan distance patterns',
        'Distance-based brightness attenuation'
    ]
}