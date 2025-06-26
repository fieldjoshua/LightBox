#!/usr/bin/env python3
"""
Music Sync 120 BPM Animation for LightBox
Creates a dynamic light show that appears synchronized to 120 BPM music
Features beat detection, rhythm patterns, and musical phrasing
"""

import math
import colorsys

def animate(pixels, config, frame):
    """
    Music-synchronized animation at 120 BPM with beat patterns and rhythm
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Music timing constants
    bpm = 120.0
    beats_per_second = bpm / 60.0
    
    # Calculate beat timing based on FPS
    beat_length_frames = config.fps / beats_per_second
    
    # Current beat position (0.0 to 1.0 within each beat)
    beat_position = (frame % beat_length_frames) / beat_length_frames
    
    # Measure timing (4 beats per measure)
    measure_frames = beat_length_frames * 4
    measure_position = (frame % measure_frames) / measure_frames
    current_beat_in_measure = int((frame % measure_frames) / beat_length_frames)
    
    # Phrase timing (16 beats = 4 measures)
    phrase_frames = measure_frames * 4
    phrase_position = (frame % phrase_frames) / phrase_frames
    
    # Beat intensity calculation (sharp attack, exponential decay)
    beat_intensity = math.exp(-beat_position * 8.0) * (1.0 - beat_position * 0.3)
    
    # Different intensity patterns for different beats in measure
    beat_multipliers = [1.0, 0.7, 0.9, 0.6]  # Kick, snare pattern
    beat_mult = beat_multipliers[current_beat_in_measure]
    beat_intensity *= beat_mult
    
    # Color cycling through the phrase (16 beats)
    base_hue = (config.hue_offset + phrase_position * 360) % 360
    
    # Musical sections - change character every 4 measures
    section = int(frame / phrase_frames) % 4
    
    total_pixels = config.matrix_width * config.matrix_height
    
    for i in range(total_pixels):
        # Get pixel coordinates
        x = i % config.matrix_width
        y = i // config.matrix_width
        
        # Normalize coordinates
        nx = x / (config.matrix_width - 1)
        ny = y / (config.matrix_height - 1)
        
        # Center distance for radial effects
        center_x = 0.5
        center_y = 0.5
        distance = math.sqrt((nx - center_x)**2 + (ny - center_y)**2)
        angle = math.atan2(ny - center_y, nx - center_x)
        
        # Different visual styles for different musical sections
        if section == 0:
            # Section 1: Radial pulses from center (verse-like)
            wave = math.sin((distance * 8.0 * config.scale) - (frame * config.speed * 0.1))
            intensity = beat_intensity * (0.5 + 0.5 * wave)
            hue = (base_hue + distance * 60) % 360
            
        elif section == 1:
            # Section 2: Vertical waves (pre-chorus build)
            wave1 = math.sin((ny * 6.0 * config.scale) - (frame * config.speed * 0.15))
            wave2 = math.sin((frame * config.speed * 0.05) + nx * 4.0)
            intensity = beat_intensity * (0.6 + 0.4 * wave1 * wave2)
            hue = (base_hue + ny * 120 + wave2 * 30) % 360
            
        elif section == 2:
            # Section 3: Spinning spiral (chorus-like)
            spiral_angle = angle + (frame * config.speed * 0.08) + (distance * 12.0 * config.scale)
            spiral_wave = math.sin(spiral_angle)
            intensity = beat_intensity * (0.7 + 0.3 * spiral_wave)
            hue = (base_hue + spiral_angle * 20 + beat_position * 60) % 360
            
        else:
            # Section 4: Corner strobes (breakdown/bridge)
            corner_dist1 = math.sqrt((nx - 0)**2 + (ny - 0)**2)
            corner_dist2 = math.sqrt((nx - 1)**2 + (ny - 1)**2)
            corner_dist3 = math.sqrt((nx - 0)**2 + (ny - 1)**2)
            corner_dist4 = math.sqrt((nx - 1)**2 + (ny - 0)**2)
            
            min_corner_dist = min(corner_dist1, corner_dist2, corner_dist3, corner_dist4)
            corner_effect = math.exp(-min_corner_dist * 6.0)
            
            # Alternate corners on different beats
            if current_beat_in_measure % 2 == 0:
                corner_effect *= (1.0 if (corner_dist1 == min_corner_dist or corner_dist2 == min_corner_dist) else 0.3)
            else:
                corner_effect *= (1.0 if (corner_dist3 == min_corner_dist or corner_dist4 == min_corner_dist) else 0.3)
            
            intensity = beat_intensity * corner_effect
            hue = (base_hue + current_beat_in_measure * 90) % 360
        
        # Apply saturation and brightness
        saturation = config.saturation * (0.8 + 0.2 * intensity)
        value = intensity * config.brightness
        
        # Add subtle high-frequency sparkle on strong beats
        if beat_position < 0.1 and beat_mult > 0.8:
            sparkle = math.sin(i * 17.3 + frame * 0.7) * 0.3
            value += sparkle * beat_intensity
        
        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue / 360.0, saturation, value)
        
        # Apply gamma correction
        gamma = config.gamma
        r = math.pow(max(0, min(1, r)), 1.0 / gamma)
        g = math.pow(max(0, min(1, g)), 1.0 / gamma)
        b = math.pow(max(0, min(1, b)), 1.0 / gamma)
        
        # Convert to 0-255 range and ensure valid values
        r = int(max(0, min(255, r * 255)))
        g = int(max(0, min(255, g * 255)))
        b = int(max(0, min(255, b * 255)))
        
        # Apply color correction
        if hasattr(config, 'correct_color'):
            r, g, b = config.correct_color(r, g, b)
        
        pixels[i] = (r, g, b)