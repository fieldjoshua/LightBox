# flake8: noqa
"""
Aurora Animation for CosmicLED
Creates flowing aurora borealis-like patterns with ethereal movement
"""

import math

def animate(pixels, config, frame):
    """
    Aurora borealis simulation with flowing curtains of light
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Animation parameters
    time_scale = config.speed * 0.06
    time_offset = frame * time_scale
    
    # Aurora characteristics
    wave_layers = 4  # Number of aurora layers
    base_height = config.matrix_height * 0.3  # Base aurora height
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            brightness = 0.0
            hue_accumulator = 0.0
            weight_total = 0.0
            
            # Create multiple aurora layers
            for layer in range(wave_layers):
                layer_offset = layer * 0.7
                layer_speed = 1.0 + layer * 0.3
                
                # Wave function for aurora curtain
                wave1 = math.sin(x * 0.3 + time_offset * layer_speed + layer_offset)
                wave2 = math.sin(x * 0.15 + time_offset * layer_speed * 0.7 + layer_offset * 1.5)
                wave3 = math.cos(x * 0.45 + time_offset * layer_speed * 1.2 + layer_offset * 0.8)
                
                # Combine waves for aurora height
                aurora_height = base_height + (wave1 + wave2 * 0.7 + wave3 * 0.5) * 2.0
                
                # Vertical falloff from aurora curtain
                distance_from_aurora = abs(y - aurora_height)
                
                # Aurora intensity with soft falloff
                aurora_intensity = math.exp(-distance_from_aurora * 0.4)
                
                # Add vertical streaming effect
                stream_wave = math.sin(y * 0.8 + time_offset * 2.0 + x * 0.1) * 0.3 + 0.7
                aurora_intensity *= stream_wave
                
                # Layer-specific color
                layer_hue = (config.hue_offset + layer * 60 + time_offset * 15) % 360
                
                # Horizontal color variation
                horizontal_shift = math.sin(x * 0.2 + time_offset * 0.8 + layer * 1.2) * 40
                final_hue = (layer_hue + horizontal_shift) % 360
                
                # Weight by intensity for color mixing
                weight = aurora_intensity * (1.0 - layer * 0.15)  # Front layers stronger
                hue_accumulator += final_hue * weight
                weight_total += weight
                
                brightness += aurora_intensity * (1.0 - layer * 0.2)
            
            # Calculate average hue
            if weight_total > 0:
                average_hue = (hue_accumulator / weight_total) % 360
            else:
                average_hue = config.hue_offset
            
            # Add subtle shimmer
            shimmer = math.sin(x * 2.3 + y * 1.7 + time_offset * 4) * 0.1 + 0.9
            brightness *= shimmer
            
            # Add atmospheric perspective (dimmer at edges)
            edge_distance = min(x, config.matrix_width - 1 - x, y, config.matrix_height - 1 - y)
            edge_factor = 1.0 - math.exp(-edge_distance * 0.5) * 0.3
            brightness *= edge_factor
            
            # Keep effect brightness in 0–1 range (global brightness applied later)
            brightness = max(0.0, min(1.0, brightness))
            
            # Get color
            if hasattr(config, 'get_palette_color'):
                palette_pos = (average_hue / 360.0) % 1.0
                r, g, b = config.get_palette_color(palette_pos)
                r = int(r * brightness)
                g = int(g * brightness)
                b = int(b * brightness)
            else:
                # Use reduced saturation for aurora effect
                aurora_saturation = config.saturation * 0.8
                r, g, b = config.hsv_to_rgb(average_hue, aurora_saturation, brightness)
            
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
    'name': 'Aurora',
    'description': 'Flowing aurora borealis with ethereal light curtains',
    'author': 'CosmicLED',
    'version': '1.0',
    'parameters': {
        'speed': 'Aurora flow speed (0.1-5.0)',
        'scale': 'Wave amplitude (0.1-3.0)',
        'hue_offset': 'Color shift (0-360 degrees)',
        'saturation': 'Color saturation (0.0-1.0)'
    },
    'features': [
        'Multiple layered aurora curtains',
        'Vertical streaming effects',
        'Soft atmospheric falloff',
        'Color mixing between layers',
        'Horizontal color variations',
        'Subtle shimmer effects'
    ]
}