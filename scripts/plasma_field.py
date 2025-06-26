# flake8: noqa
"""
Plasma Field Animation for CosmicLED
Creates electric plasma-like effects with energy tendrils and electromagnetic fields
"""

import math

def animate(pixels, config, frame):
    """
    Plasma field simulation with electromagnetic effects
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Animation parameters
    time_scale = config.speed * 0.1
    field_scale = config.scale * 2.0
    time_offset = frame * time_scale
    
    # Plasma field parameters
    field_sources = 4  # Number of plasma sources
    electrical_frequency = 8.0
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            # Normalize coordinates
            nx = (x - config.matrix_width/2) / config.matrix_width
            ny = (y - config.matrix_height/2) / config.matrix_height
            
            total_field_strength = 0.0
            electrical_accumulator = 0.0
            
            # Create plasma field sources
            for source_id in range(field_sources):
                # Source position (orbiting)
                orbit_phase = source_id * 2 * math.pi / field_sources + time_offset * 0.7
                source_x = math.cos(orbit_phase) * 0.3
                source_y = math.sin(orbit_phase * 1.3) * 0.3  # Different Y frequency
                
                # Distance to source
                dx = nx - source_x
                dy = ny - source_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0.01:  # Avoid division by zero
                    # Electromagnetic field strength (inverse square law)
                    field_strength = 1.0 / (1.0 + distance * field_scale)
                    
                    # Electric field lines
                    field_angle = math.atan2(dy, dx)
                    field_oscillation = math.sin(distance * electrical_frequency + time_offset * 4.0 + source_id)
                    
                    # Field strength with oscillation
                    oscillating_field = field_strength * (field_oscillation * 0.5 + 0.5)
                    total_field_strength += oscillating_field
                    
                    # Electrical discharge patterns
                    discharge_pattern = math.sin(distance * 12.0 + time_offset * 6.0 + field_angle * 3.0)
                    electrical_accumulator += oscillating_field * discharge_pattern
            
            # Plasma interference patterns
            interference1 = math.sin(nx * 8.0 + time_offset * 2.0)
            interference2 = math.sin(ny * 6.0 + time_offset * 1.5)
            interference3 = math.sin((nx + ny) * 5.0 + time_offset * 2.5)
            
            interference_pattern = (interference1 + interference2 + interference3) / 3.0
            
            # Standing wave patterns
            standing_wave_x = math.sin(nx * 10.0 + time_offset * 3.0)
            standing_wave_y = math.cos(ny * 8.0 + time_offset * 2.0)
            standing_waves = standing_wave_x * standing_wave_y
            
            # Electric arc simulation
            arc_probability = total_field_strength * 0.3
            arc_intensity = 0.0
            
            if arc_probability > 0.4:  # Threshold for arc formation
                arc_noise = math.sin(x * 7.3 + y * 5.7 + time_offset * 10.0)
                if arc_noise > 0.6:  # Random arc formation
                    arc_intensity = (arc_noise - 0.6) * 2.5  # Scale arc intensity
            
            # Combine all plasma effects
            plasma_brightness = (
                total_field_strength * 0.4 +
                abs(interference_pattern) * 0.3 +
                abs(standing_waves) * 0.2 +
                arc_intensity * 0.6 +
                abs(electrical_accumulator) * 0.2
            )
            
            # Add plasma glow effect
            glow_distance = math.sqrt(nx**2 + ny**2)
            plasma_glow = math.exp(-glow_distance * 2.0) * 0.3
            plasma_brightness += plasma_glow
            
            # Keep effect brightness in 0–1 range (global brightness applied later)
            final_brightness = max(0.0, min(1.0, plasma_brightness))
            
            # Color based on field characteristics
            if arc_intensity > 0.1:
                # Electric arcs are white/blue
                pixel_hue = (config.hue_offset + 240) % 360  # Blue
                saturation = 0.8
            elif total_field_strength > 0.5:
                # Strong fields are purple/magenta
                pixel_hue = (config.hue_offset + 300 + electrical_accumulator * 30) % 360
                saturation = config.saturation
            else:
                # Background plasma varies through spectrum
                field_color = (total_field_strength + interference_pattern) * 180
                pixel_hue = (config.hue_offset + field_color + time_offset * 30) % 360
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
            
            # Add electric white flash for strong arcs
            if arc_intensity > 0.3:
                flash_amount = (arc_intensity - 0.3) * 2.0
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
    'name': 'Plasma Field',
    'description': 'Electric plasma effects with electromagnetic fields',
    'author': 'CosmicLED',
    'version': '1.0',
    'parameters': {
        'speed': 'Field oscillation speed (0.1-5.0)',
        'scale': 'Field intensity (0.1-3.0)',
        'hue_offset': 'Color shift (0-360 degrees)',
        'saturation': 'Color saturation (0.0-1.0)'
    },
    'features': [
        'Multiple orbiting plasma sources',
        'Electromagnetic field simulation',
        'Electric arc effects',
        'Interference patterns',
        'Standing wave formations',
        'Dynamic color based on field strength'
    ]
}