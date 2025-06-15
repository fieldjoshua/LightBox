"""
Shimmer Animation for CosmicLED
Creates a shimmering wave effect across the LED matrix
"""

import math
import random

def animate(pixels, config, frame):
    """
    Shimmer animation with wave-like brightness variations
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Animation parameters
    wave_speed = config.speed * 0.15
    wave_scale = config.scale * 0.8
    time_offset = frame * wave_speed
    
    # Shimmer intensity and frequency
    shimmer_frequency = 0.3
    shimmer_intensity = 0.4
    
    # Base color from palette
    base_hue = (config.hue_offset + frame * 0.5) % 360
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            # Create primary wave pattern
            wave1 = math.sin((x * wave_scale + time_offset) * 0.4)
            wave2 = math.sin((y * wave_scale + time_offset * 0.8) * 0.3)
            wave3 = math.cos((x + y) * wave_scale * 0.2 + time_offset * 0.6)
            
            # Combine waves for base brightness
            base_brightness = (wave1 + wave2 + wave3) / 3 * 0.5 + 0.5
            
            # Add shimmer effect with high-frequency noise
            shimmer_noise = math.sin((x * 2.3 + y * 1.7 + frame * 0.3) * shimmer_frequency)
            shimmer_effect = shimmer_noise * shimmer_intensity
            
            # Add random sparkle points
            sparkle_chance = 0.05  # 5% chance per pixel per frame
            sparkle_boost = 0
            if random.random() < sparkle_chance:
                sparkle_boost = random.uniform(0.3, 0.8)
            
            # Calculate final brightness
            final_brightness = base_brightness + shimmer_effect + sparkle_boost
            final_brightness = max(0.1, min(1.0, final_brightness))
            
            # Color variation based on position
            hue_variation = math.sin(x * 0.2 + y * 0.15 + time_offset * 0.1) * 30
            pixel_hue = (base_hue + hue_variation) % 360
            
            # Apply brightness scaling
            brightness_scaled = final_brightness * config.brightness_scale
            
            # Get color from palette or HSV
            if hasattr(config, 'get_palette_color'):
                # Use palette color with brightness modulation
                palette_pos = (pixel_hue / 360.0) % 1.0
                r, g, b = config.get_palette_color(palette_pos)
                
                # Apply brightness
                r = int(r * brightness_scaled)
                g = int(g * brightness_scaled)
                b = int(b * brightness_scaled)
            else:
                # Fallback to HSV conversion
                r, g, b = config.hsv_to_rgb(
                    pixel_hue, 
                    config.saturation, 
                    brightness_scaled
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

# Animation metadata (optional, for display in web interface)
ANIMATION_INFO = {
    'name': 'Shimmer',
    'description': 'Shimmering wave effect with sparkles',
    'author': 'CosmicLED',
    'version': '1.0',
    'parameters': {
        'speed': 'Animation speed (0.1-5.0)',
        'scale': 'Wave scale (0.1-3.0)',
        'brightness_scale': 'Overall brightness (0.0-2.0)',
        'hue_offset': 'Color shift (0-360 degrees)',
        'saturation': 'Color saturation (0.0-1.0)'
    }
}