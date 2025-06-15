"""
Feathers BPM Animation for CosmicLED
Feather patterns synchronized to 120 BPM music
"""

import math

def animate(pixels, config, frame):
    """
    Feathery patterns synchronized to 120 BPM (2 beats per second)
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # BPM synchronization (120 BPM = 2 beats per second)
    bpm = 120
    beats_per_second = bpm / 60.0
    seconds_per_beat = 1.0 / beats_per_second
    frames_per_beat = config.fps * seconds_per_beat
    
    # Calculate beat timing
    beat_progress = (frame % frames_per_beat) / frames_per_beat
    beat_number = frame // frames_per_beat
    
    # Different beat patterns
    beat_intensity = math.sin(beat_progress * 2 * math.pi) * 0.5 + 0.5
    kick_beat = 1.0 if beat_progress < 0.1 else 0.0  # Sharp kick on beat
    
    # Animation parameters synced to BPM
    time_scale = config.speed * beats_per_second * 0.5
    pattern_scale = config.scale * 1.5
    time_offset = frame * time_scale / config.fps
    
    # Feather characteristics that pulse with beat
    feather_count = 3
    feather_spread = 2.5 + beat_intensity * 1.0  # Spread pulses with beat
    barbule_frequency = 4.0 + kick_beat * 2.0  # Barbules get sharper on kick
    
    # Matrix center
    center_x = config.matrix_width / 2.0
    center_y = config.matrix_height / 2.0
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx**2 + dy**2)
            angle = math.atan2(dy, dx)
            
            brightness = 0.0
            
            for feather_id in range(feather_count):
                # Feather rotation synced to beat
                beat_rotation = beat_number * 0.5  # Slow rotation between beats
                feather_angle = (feather_id * 2 * math.pi / feather_count) + beat_rotation
                spine_angle = feather_angle
                
                rotated_angle = angle - spine_angle
                spine_alignment = math.cos(rotated_angle)
                
                if spine_alignment > 0:
                    spine_strength = spine_alignment ** 2
                    spine_distance = distance * spine_alignment
                    perp_distance = distance * math.sin(rotated_angle)
                    
                    # Barbule pattern synced to beat subdivisions
                    barbule_phase = spine_distance * barbule_frequency + beat_progress * 4 * math.pi
                    barbule_wave = math.sin(barbule_phase)
                    barbule_envelope = math.exp(-abs(perp_distance) * feather_spread)
                    
                    # Feather tip extends/contracts with beat
                    tip_extension = 0.3 + beat_intensity * 0.4
                    tip_falloff = math.exp(-spine_distance * tip_extension)
                    
                    # Width pulses with beat
                    width_base = 0.7 + beat_intensity * 0.3
                    width_variation = math.sin(spine_distance * 2 + beat_progress * 2 * math.pi) * 0.3 + width_base
                    
                    # Beat emphasis on kick
                    kick_emphasis = 1.0 + kick_beat * 0.5
                    
                    feather_intensity = (
                        spine_strength * 
                        barbule_envelope * 
                        tip_falloff * 
                        width_variation *
                        (barbule_wave * 0.5 + 0.8) *
                        kick_emphasis
                    )
                    
                    brightness += feather_intensity * 0.6
            
            # Beat-synchronized background texture
            bg_phase = x * 0.5 + y * 0.4 + beat_progress * 2 * math.pi
            background_texture = math.sin(bg_phase) * 0.1 + 0.1
            brightness += background_texture
            
            # Apply beat intensity scaling
            brightness *= (0.7 + beat_intensity * 0.3)
            brightness = max(0.0, min(1.0, brightness * config.brightness_scale))
            
            # Color shifts with beat progression
            hue_base = (config.hue_offset + beat_number * 15) % 360
            beat_hue_shift = beat_intensity * 30
            hue_variation = (
                math.sin(x * 0.3 + beat_progress * math.pi) * 20 +
                math.sin(y * 0.25 + beat_progress * math.pi * 0.7) * 15
            )
            pixel_hue = (hue_base + beat_hue_shift + hue_variation) % 360
            
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
                    pixels[pixel_index] = (r, g, b)
                else:
                    pixels[pixel_index] = (r, g, b)
            except IndexError:
                pass

# Animation metadata
ANIMATION_INFO = {
    'name': 'Feathers BPM',
    'description': 'Feather patterns synchronized to 120 BPM music',
    'author': 'CosmicLED',
    'version': '1.0',
    'bpm': 120,
    'parameters': {
        'speed': 'Beat sync multiplier (0.5-2.0 recommended)',
        'scale': 'Feather size (0.1-3.0)',
        'brightness_scale': 'Beat intensity (0.0-2.0)',
        'hue_offset': 'Color shift (0-360 degrees)',
        'saturation': 'Color saturation (0.0-1.0)'
    },
    'features': [
        '120 BPM synchronization',
        'Beat-responsive feather spread',
        'Kick drum emphasis',
        'Color progression with beats',
        'Pulsing barbule patterns'
    ]
}