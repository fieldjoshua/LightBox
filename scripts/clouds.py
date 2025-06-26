# flake8: noqa
"""
Clouds Animation - Puffy white clouds slowly drifting across a blue sky
Creates a peaceful sky scene with realistic cloud movement and depth
"""

import math
import random
from typing import List, Tuple

def animate(pixels, config, frame):
    """
    Animate puffy white clouds slowly passing across a blue sky
    
    Args:
        pixels: LED pixel array to update
        config: Configuration object with settings
        frame: Current frame number for animation timing
    """
    
    # Get matrix dimensions
    width = getattr(config, 'matrix_width', 10)
    height = getattr(config, 'matrix_height', 10)
    
    # Animation parameters
    speed = getattr(config, 'speed', 1.0) * 0.3  # Slow cloud movement
    scale = getattr(config, 'scale', 1.0)
    
    # Sky colors
    sky_blue = (135, 206, 235)  # Light blue sky
    cloud_white = (255, 255, 255)  # Pure white clouds
    cloud_shadow = (240, 248, 255)  # Light gray cloud shadows
    
    # Time-based animation
    time = frame * speed * 0.02
    
    # Cloud parameters
    cloud_layers = [
        {
            'offset': time * 0.5,
            'size': 2.5 * scale,
            'density': 0.6,
            'height_bias': 0.3,
            'brightness': 1.0
        },
        {
            'offset': time * 0.3,
            'size': 3.0 * scale,
            'density': 0.4,
            'height_bias': 0.6,
            'brightness': 0.8
        },
        {
            'offset': time * 0.7,
            'size': 1.8 * scale,
            'density': 0.5,
            'height_bias': 0.1,
            'brightness': 0.9
        }
    ]
    
    # Generate clouds for each pixel
    for y in range(height):
        for x in range(width):
            # Normalize coordinates
            nx = x / width
            ny = y / height
            
            # Start with sky blue
            final_color = list(sky_blue)
            
            # Add cloud layers
            cloud_intensity = 0.0
            
            for layer in cloud_layers:
                # Cloud noise generation
                cloud_value = generate_cloud_noise(
                    nx + layer['offset'], 
                    ny + layer['height_bias'], 
                    layer['size'], 
                    layer['density']
                )
                
                # Bias clouds toward upper portion of sky
                height_factor = 1.0 - (ny * 0.7)  # Fade clouds toward bottom
                cloud_value *= height_factor
                
                # Apply layer brightness
                cloud_value *= layer['brightness']
                
                cloud_intensity += cloud_value
            
            # Clamp cloud intensity
            cloud_intensity = min(cloud_intensity, 1.0)
            
            # Blend sky and clouds
            if cloud_intensity > 0.1:
                # Use white clouds with subtle shadows
                if cloud_intensity > 0.7:
                    cloud_color = cloud_white
                else:
                    cloud_color = cloud_shadow
                
                # Blend based on cloud intensity
                blend_factor = cloud_intensity
                final_color = [
                    int(sky_blue[i] * (1 - blend_factor) + cloud_color[i] * blend_factor)
                    for i in range(3)
                ]
            
            # Apply gamma correction (global brightness applied later)
            gamma = getattr(config, 'gamma', 2.2)
            final_color = [int(pow(c / 255.0, 1/gamma) * 255) for c in final_color]
            
            # Set pixel color
            pixel_index = config.xy_to_index(x, y)
            brightness = getattr(config, 'brightness', 1.0)
            pixels[pixel_index] = (
                int(max(0, min(255, final_color[0] * brightness))),
                int(max(0, min(255, final_color[1] * brightness))),
                int(max(0, min(255, final_color[2] * brightness)))
            )

def generate_cloud_noise(x: float, y: float, scale: float, density: float) -> float:
    """
    Generate realistic cloud-like noise using multiple octaves of Perlin-style noise
    
    Args:
        x, y: Coordinates
        scale: Size of cloud features
        density: Overall cloud coverage
    
    Returns:
        Cloud intensity value (0.0 to 1.0)
    """
    
    # Multi-octave noise for realistic cloud shapes
    noise_value = 0.0
    amplitude = 1.0
    frequency = 1.0 / scale
    
    # Add multiple noise octaves
    for octave in range(4):
        # Simple noise approximation using sine waves
        noise_layer = (
            math.sin(x * frequency * 6.28) * 
            math.cos(y * frequency * 6.28) * 
            math.sin((x + y) * frequency * 4.0)
        )
        
        # Add turbulence
        turbulence = (
            math.sin(x * frequency * 12.56 + octave) * 
            math.cos(y * frequency * 12.56 + octave * 1.7)
        )
        
        noise_layer = (noise_layer + turbulence * 0.5) / 1.5
        
        noise_value += noise_layer * amplitude
        amplitude *= 0.5
        frequency *= 2.0
    
    # Normalize and apply density
    noise_value = (noise_value + 1.0) / 2.0  # Normalize to 0-1
    
    # Create puffy cloud shapes
    cloud_threshold = 1.0 - density
    if noise_value > cloud_threshold:
        # Soft cloud edges
        cloud_intensity = (noise_value - cloud_threshold) / density
        cloud_intensity = smooth_step(cloud_intensity)
        return cloud_intensity
    
    return 0.0

def smooth_step(x: float) -> float:
    """
    Smooth interpolation function for soft cloud edges
    """
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)

# Animation metadata
ANIMATION_NAME = "Clouds"
ANIMATION_DESCRIPTION = "Puffy white clouds slowly drifting across a blue sky"
ANIMATION_AUTHOR = "Claude"
ANIMATION_VERSION = "1.0"