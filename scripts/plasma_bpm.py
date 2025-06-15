"""
Plasma BPM Animation for CosmicLED
Electric plasma effects synchronized to 120 BPM music
"""

import math

def animate(pixels, config, frame):
    """
    Plasma field effects synchronized to 120 BPM (2 beats per second)
    
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
    
    # Beat patterns
    beat_intensity = math.sin(beat_progress * 2 * math.pi) * 0.5 + 0.5
    kick_beat = 1.0 if beat_progress < 0.15 else 0.0  # Sharp kick
    snare_beat = 1.0 if 0.45 < beat_progress < 0.6 else 0.0  # Snare on off-beat
    
    # Animation parameters synced to BPM
    time_scale = config.speed * beats_per_second
    field_scale = config.scale * 2.0
    time_offset = frame * time_scale / config.fps
    
    # Plasma parameters that respond to beat
    field_sources = 4
    electrical_frequency = 8.0 + kick_beat * 4.0  # Higher frequency on kick
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            nx = (x - config.matrix_width/2) / config.matrix_width
            ny = (y - config.matrix_height/2) / config.matrix_height
            
            total_field_strength = 0.0
            electrical_accumulator = 0.0
            
            # Plasma sources move to beat
            for source_id in range(field_sources):
                # Beat-synchronized orbiting
                beat_orbit_speed = beats_per_second * 0.25
                orbit_phase = source_id * 2 * math.pi / field_sources + time_offset * beat_orbit_speed
                
                # Kick makes sources expand outward
                orbit_radius = 0.3 + kick_beat * 0.2
                source_x = math.cos(orbit_phase) * orbit_radius
                source_y = math.sin(orbit_phase * 1.3) * orbit_radius
                
                dx = nx - source_x
                dy = ny - source_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0.01:
                    # Field strength pulses with beat
                    base_field = 1.0 / (1.0 + distance * field_scale)
                    beat_modulation = 1.0 + beat_intensity * 0.5
                    field_strength = base_field * beat_modulation
                    
                    # Electric oscillations synced to beat subdivisions
                    field_angle = math.atan2(dy, dx)
                    electric_phase = distance * electrical_frequency + beat_progress * 8 * math.pi + source_id * math.pi
                    field_oscillation = math.sin(electric_phase)
                    
                    # Kick creates electric surges
                    surge_intensity = 1.0 + kick_beat * 1.5
                    oscillating_field = field_strength * (field_oscillation * 0.5 + 0.5) * surge_intensity
                    total_field_strength += oscillating_field
                    
                    # Snare creates secondary discharge patterns
                    snare_discharge = math.sin(distance * 15.0 + beat_progress * 12 * math.pi + field_angle * 4.0)
                    snare_effect = snare_beat * snare_discharge * 0.3
                    electrical_accumulator += oscillating_field * (snare_discharge + snare_effect)
            
            # Beat-synchronized interference patterns
            interference_freq = 4.0 + beat_intensity * 4.0
            interference1 = math.sin(nx * interference_freq * 2 + beat_progress * 4 * math.pi)
            interference2 = math.sin(ny * interference_freq * 1.5 + beat_progress * 3 * math.pi)
            interference3 = math.sin((nx + ny) * interference_freq + beat_progress * 5 * math.pi)
            
            interference_pattern = (interference1 + interference2 + interference3) / 3.0
            
            # Standing waves that pulse with beat
            wave_amplitude = 1.0 + beat_intensity * 0.8
            standing_wave_x = math.sin(nx * 10.0 + beat_progress * 6 * math.pi) * wave_amplitude
            standing_wave_y = math.cos(ny * 8.0 + beat_progress * 4 * math.pi) * wave_amplitude
            standing_waves = standing_wave_x * standing_wave_y
            
            # Electric arcs triggered by kicks and snares
            arc_threshold = 0.4 - kick_beat * 0.2 - snare_beat * 0.1  # Lower threshold on beats
            arc_probability = total_field_strength * 0.3
            arc_intensity = 0.0
            
            if arc_probability > arc_threshold:
                # Beat-synchronized arc noise
                arc_phase = x * 7.3 + y * 5.7 + beat_progress * 20 * math.pi
                arc_noise = math.sin(arc_phase)
                arc_trigger_threshold = 0.6 - kick_beat * 0.3  # Easier to trigger on kick
                
                if arc_noise > arc_trigger_threshold:
                    arc_base_intensity = (arc_noise - arc_trigger_threshold) * 2.5
                    # Amplify arcs on beats
                    beat_arc_multiplier = 1.0 + kick_beat * 2.0 + snare_beat * 1.0
                    arc_intensity = arc_base_intensity * beat_arc_multiplier
            
            # Combine plasma effects with beat emphasis
            plasma_brightness = (
                total_field_strength * 0.4 +
                abs(interference_pattern) * 0.3 +
                abs(standing_waves) * 0.2 +
                arc_intensity * 0.6 +
                abs(electrical_accumulator) * 0.2
            )
            
            # Beat-synchronized plasma glow
            glow_distance = math.sqrt(nx**2 + ny**2)
            glow_intensity = 0.3 + beat_intensity * 0.2
            plasma_glow = math.exp(-glow_distance * 2.0) * glow_intensity
            plasma_brightness += plasma_glow
            
            # Apply brightness scaling with beat emphasis
            beat_brightness_boost = 0.8 + beat_intensity * 0.4 + kick_beat * 0.3
            final_brightness = max(0.0, min(1.0, plasma_brightness * config.brightness_scale * beat_brightness_boost))
            
            # Color changes with beat progression
            if arc_intensity > 0.1:
                # Arcs flash brighter on beats
                arc_hue = (config.hue_offset + 240 + kick_beat * 60) % 360
                pixel_hue = arc_hue
                saturation = 0.8 - kick_beat * 0.3  # More white on kick
            elif total_field_strength > 0.5:
                # Strong fields shift color with beat
                beat_color_shift = beat_number * 20 + beat_intensity * 40
                field_hue = (config.hue_offset + 300 + beat_color_shift + electrical_accumulator * 30) % 360
                pixel_hue = field_hue
                saturation = config.saturation
            else:
                # Background plasma cycles through spectrum with beat
                spectrum_position = (beat_number * 30 + beat_progress * 120) % 360
                field_color = (total_field_strength + interference_pattern) * 60
                pixel_hue = (config.hue_offset + spectrum_position + field_color) % 360
                saturation = config.saturation * 0.9
            
            # Get color
            if hasattr(config, 'get_palette_color'):
                palette_pos = (pixel_hue / 360.0) % 1.0
                r, g, b = config.get_palette_color(palette_pos)
                r = int(r * final_brightness)
                g = int(g * final_brightness)
                b = int(b * final_brightness)
            else:
                r, g, b = config.hsv_to_rgb(pixel_hue, saturation, final_brightness)
            
            # Electric white flash for strong arcs on beats
            if arc_intensity > 0.3:
                flash_amount = (arc_intensity - 0.3) * 2.0
                beat_flash_boost = 1.0 + kick_beat * 0.5
                flash_amount *= beat_flash_boost
                r = int(r + (255 - r) * flash_amount)
                g = int(g + (255 - g) * flash_amount)
                b = int(b + (255 - b) * flash_amount)
            
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
    'name': 'Plasma BPM',
    'description': 'Electric plasma synchronized to 120 BPM music',
    'author': 'CosmicLED',
    'version': '1.0',
    'bpm': 120,
    'parameters': {
        'speed': 'Beat sync multiplier (0.5-2.0 recommended)',
        'scale': 'Field intensity (0.1-3.0)',
        'brightness_scale': 'Plasma brightness (0.0-2.0)',
        'hue_offset': 'Color shift (0-360 degrees)',
        'saturation': 'Color saturation (0.0-1.0)'
    },
    'features': [
        '120 BPM synchronization',
        'Kick drum plasma surges',
        'Snare beat discharge patterns',
        'Beat-responsive electric arcs',
        'Color progression with rhythm',
        'Standing wave amplification'
    ]
}