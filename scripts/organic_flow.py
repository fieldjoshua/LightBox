# flake8: noqa
"""
Organic Flow Animation for CosmicLED
Creates fluid, organic patterns inspired by cellular structures and flowing liquids
"""

import math

def animate(pixels, config, frame):
    """
    Organic flowing patterns with cellular and fluid dynamics
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Animation parameters
    time_scale = config.speed * 0.05
    pattern_scale = config.scale * 1.2
    time_offset = frame * time_scale
    
    # Organic flow parameters
    cell_count = 5  # Number of flow centers
    flow_strength = 2.0
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            # Normalize coordinates
            nx = x / config.matrix_width
            ny = y / config.matrix_height
            
            brightness = 0.0
            flow_vectors_x = 0.0
            flow_vectors_y = 0.0
            
            # Create multiple organic flow centers
            for cell_id in range(cell_count):
                # Flow center position (moves organically)
                center_phase_x = cell_id * 2.13 + time_offset * 0.8
                center_phase_y = cell_id * 3.17 + time_offset * 0.6
                
                center_x = 0.5 + math.sin(center_phase_x) * 0.3
                center_y = 0.5 + math.cos(center_phase_y) * 0.3
                
                # Distance to flow center
                dx = nx - center_x
                dy = ny - center_y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0:
                    # Organic flow field
                    flow_influence = math.exp(-distance * 4.0)
                    
                    # Create swirling motion
                    angle = math.atan2(dy, dx)
                    swirl_angle = angle + time_offset * 2.0 + distance * 8.0
                    
                    # Flow vectors
                    flow_x = math.cos(swirl_angle) * flow_influence
                    flow_y = math.sin(swirl_angle) * flow_influence
                    
                    flow_vectors_x += flow_x
                    flow_vectors_y += flow_y
                    
                    # Cell core brightness
                    core_brightness = flow_influence * (1.0 - distance * 2.0)
                    brightness += max(0, core_brightness)
            
            # Apply flow field to create organic patterns
            flow_magnitude = math.sqrt(flow_vectors_x**2 + flow_vectors_y**2)
            flow_pattern = math.sin(flow_magnitude * 6.0 + time_offset * 3.0) * 0.5 + 0.5
            
            # Cellular texture
            cell_scale = 3.0 * pattern_scale
            cell_pattern1 = math.sin(nx * cell_scale * math.pi + flow_vectors_x * 4.0)
            cell_pattern2 = math.sin(ny * cell_scale * math.pi + flow_vectors_y * 4.0)
            cell_pattern3 = math.sin((nx + ny) * cell_scale * 0.7 * math.pi + time_offset * 2.0)
            
            cellular_texture = (cell_pattern1 * cell_pattern2 * cell_pattern3) * 0.3 + 0.7
            
            # Membrane-like structures
            membrane_thickness = 0.1
            membrane_pattern = 0.0
            
            for membrane_id in range(3):
                membrane_phase = membrane_id * 2.1 + time_offset * 0.4
                membrane_wave = math.sin(nx * 4.0 + membrane_phase) + math.sin(ny * 3.5 + membrane_phase * 1.3)
                membrane_distance = abs(membrane_wave) - 1.0
                
                if abs(membrane_distance) < membrane_thickness:
                    membrane_intensity = 1.0 - abs(membrane_distance) / membrane_thickness
                    membrane_pattern += membrane_intensity * 0.4
            
            # Combine all patterns
            final_brightness = (
                brightness * 0.4 +
                flow_pattern * cellular_texture * 0.4 +
                membrane_pattern * 0.3
            )
            
            # Add organic pulsing
            pulse_phase = time_offset * 1.5 + nx * 2.0 + ny * 1.5
            pulse = math.sin(pulse_phase) * 0.2 + 0.8
            final_brightness *= pulse
            
            # Keep effect brightness in 0–1 range (global brightness applied later)
            final_brightness = max(0.0, min(1.0, final_brightness))
            
            # Color based on flow dynamics
            flow_angle = math.atan2(flow_vectors_y, flow_vectors_x)
            flow_hue = (math.degrees(flow_angle) + 180) % 360
            
            base_hue = (config.hue_offset + flow_hue * 0.5 + time_offset * 10) % 360
            
            # Add color variation based on pattern type
            if membrane_pattern > 0.1:
                # Membrane areas get shifted hue
                pixel_hue = (base_hue + 60) % 360
            else:
                # Flow areas use base hue with variation
                hue_variation = cellular_texture * 40
                pixel_hue = (base_hue + hue_variation) % 360
            
            # Get color
            if hasattr(config, 'get_palette_color'):
                palette_pos = (pixel_hue / 360.0) % 1.0
                r, g, b = config.get_palette_color(palette_pos)
                r = int(r * final_brightness)
                g = int(g * final_brightness)
                b = int(b * final_brightness)
            else:
                r, g, b = config.hsv_to_rgb(pixel_hue, config.saturation, final_brightness)
            
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
    'name': 'Organic Flow',
    'description': 'Fluid organic patterns with cellular structures',
    'author': 'CosmicLED',
    'version': '1.0',
    'parameters': {
        'speed': 'Flow speed (0.1-5.0)',
        'scale': 'Pattern scale (0.1-3.0)',
        'hue_offset': 'Color shift (0-360 degrees)',
        'saturation': 'Color saturation (0.0-1.0)'
    },
    'features': [
        'Multiple organic flow centers',
        'Swirling fluid dynamics',
        'Cellular texture patterns',
        'Membrane-like structures',
        'Dynamic color based on flow',
        'Organic pulsing effects'
    ]
}