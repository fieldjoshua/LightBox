# flake8: noqa
"""
Zen Garden - A mellow, meditative visual experience
Gentle flowing water ripples, soft gradient waves, and peaceful color transitions
Perfect for relaxation and ambient lighting
"""

import math
import random
from typing import Tuple

def animate(pixels, config, frame):
    """
    Create a peaceful, flowing zen garden animation
    
    Features:
    - Gentle water ripples from multiple points
    - Soft color gradients that slowly shift
    - Calm breathing-like pulsing
    - Smooth, organic movements
    """
    
    # Get matrix dimensions
    width = getattr(config, 'matrix_width', 10)
    height = getattr(config, 'matrix_height', 10)
    
    # Very slow, gentle animation
    speed = getattr(config, 'speed', 1.0) * 0.15  # Much slower than normal
    scale = getattr(config, 'scale', 1.0)
    
    # Gentle time progression
    time = frame * speed * 0.02
    
    # Soft, calming color palette
    palette = get_zen_palette()
    
    for y in range(height):
        for x in range(width):
            # Normalize coordinates to 0-1
            nx = x / max(width - 1, 1)
            ny = y / max(height - 1, 1)
            
            # Create gentle ripples from multiple points
            ripple_intensity = create_ripples(nx, ny, time, scale)
            
            # Add soft breathing effect
            breathing = create_breathing_wave(nx, ny, time)
            
            # Gentle gradient waves
            gradient_wave = create_gradient_wave(nx, ny, time)
            
            # Combine all effects smoothly
            total_intensity = (
                ripple_intensity * 0.4 + 
                breathing * 0.3 + 
                gradient_wave * 0.3
            )
            
            # Ensure gentle intensity (no harsh bright spots)
            total_intensity = soft_clamp(total_intensity)
            
            # Get color from palette based on position and time
            color_index = (
                total_intensity + 
                nx * 0.2 + 
                ny * 0.2 + 
                time * 0.1
            ) % 1.0
            
            final_color = interpolate_palette(palette, color_index)
            
            # Apply gentle gamma (global brightness applied later)
            gamma = getattr(config, 'gamma', 1.8)  # Gentler gamma
            final_color = [int(pow(c / 255.0, 1/gamma) * 255) for c in final_color]
            
            # Set pixel
            pixel_index = config.xy_to_index(x, y)
            if pixel_index < len(pixels):
                pixels[pixel_index] = (
                    int(max(0, min(255, final_color[0]))),
                    int(max(0, min(255, final_color[1]))),
                    int(max(0, min(255, final_color[2]))),
                )

def create_ripples(x: float, y: float, time: float, scale: float) -> float:
    """Create gentle water ripples from multiple points"""
    
    # Multiple ripple sources for organic feel
    ripple_sources = [
        (0.3, 0.3, time * 0.8),      # Top-left
        (0.7, 0.7, time * 0.6),      # Bottom-right  
        (0.2, 0.8, time * 1.0),      # Bottom-left
        (0.8, 0.2, time * 0.7),      # Top-right
        (0.5, 0.5, time * 0.4),      # Center (very slow)
    ]
    
    total_ripple = 0.0
    
    for rx, ry, rt in ripple_sources:
        # Distance from ripple source
        dx = (x - rx) * scale
        dy = (y - ry) * scale
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Gentle ripple wave
        ripple_wave = math.sin(distance * 8.0 - rt * 3.0)
        
        # Soft falloff (no harsh edges)
        falloff = 1.0 / (1.0 + distance * 2.0)
        
        total_ripple += ripple_wave * falloff
    
    # Normalize and soften
    return soft_clamp(total_ripple / len(ripple_sources))

def create_breathing_wave(x: float, y: float, time: float) -> float:
    """Create a gentle breathing-like pulsing effect"""
    
    # Very slow breathing rhythm
    breath_cycle = math.sin(time * 0.5) * 0.5 + 0.5
    
    # Gentle radial gradient from center
    center_x, center_y = 0.5, 0.5
    distance_from_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
    
    # Soft radial falloff
    radial_intensity = 1.0 - soft_clamp(distance_from_center * 1.5)
    
    return breath_cycle * radial_intensity

def create_gradient_wave(x: float, y: float, time: float) -> float:
    """Create gentle flowing gradient waves"""
    
    # Multiple slow-moving gradient waves
    wave1 = math.sin(x * 2.0 + time * 0.3) * 0.5 + 0.5
    wave2 = math.cos(y * 2.5 + time * 0.4) * 0.5 + 0.5
    wave3 = math.sin((x + y) * 1.5 + time * 0.2) * 0.5 + 0.5
    
    # Combine waves gently
    combined = (wave1 + wave2 + wave3) / 3.0
    
    return soft_clamp(combined)

def soft_clamp(value: float) -> float:
    """Gently clamp values to create softer, more organic feel"""
    # Smooth clamping function
    if value < 0:
        return 0
    elif value > 1:
        return 1
    else:
        # Apply soft curve for more organic feel
        return value * value * (3.0 - 2.0 * value)  # Smoothstep

def get_zen_palette() -> list:
    """Return a calming color palette for zen atmosphere"""
    return [
        # Deep ocean blues
        (0, 20, 40),
        (10, 40, 80),
        (20, 60, 120),
        
        # Soft teals
        (30, 80, 100),
        (40, 100, 120),
        (60, 120, 140),
        
        # Gentle purples
        (80, 60, 140),
        (100, 80, 160),
        (120, 100, 180),
        
        # Soft lavenders
        (140, 120, 200),
        (160, 140, 220),
        (180, 160, 240),
        
        # Back to deep blues for smooth loop
        (100, 80, 160),
        (60, 40, 120),
        (20, 20, 80),
    ]

def interpolate_palette(palette: list, position: float) -> Tuple[int, int, int]:
    """Smoothly interpolate between palette colors"""
    
    # Normalize position to palette range
    position = position % 1.0
    palette_pos = position * (len(palette) - 1)
    
    # Get surrounding colors
    index1 = int(palette_pos)
    index2 = (index1 + 1) % len(palette)
    
    # Interpolation factor
    factor = palette_pos - index1
    
    # Smooth interpolation
    factor = factor * factor * (3.0 - 2.0 * factor)  # Smoothstep
    
    color1 = palette[index1]
    color2 = palette[index2]
    
    # Interpolate each color channel
    final_color = [
        color1[i] * (1 - factor) + color2[i] * factor
        for i in range(3)
    ]
    
    return tuple(final_color)

# Animation metadata
ANIMATION_NAME = "Zen Garden"
ANIMATION_DESCRIPTION = "Peaceful, meditative animation with gentle ripples and soft color transitions"
ANIMATION_AUTHOR = "Claude"
ANIMATION_VERSION = "1.0"