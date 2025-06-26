#!/usr/bin/env python3
"""
Enhanced Cosmic Nebulas Animation for LightBox
Beautiful nebula formations with varied shapes, dramatic contrasts, and seamless transitions
Features:
- 6 distinct nebula types: circular, spiral, ring, cloud, asymmetric, and binary
- 2-minute seamless transitions with 5-minute display cycles
- Dramatic color contrasts with enhanced saturation
- Subtle breathing effects without individual pixel on/off
- Shape-specific transformations for varied formations
- Enhanced turbulence and color variations
"""

import math
import colorsys
import random

# Animation metadata for dynamic web GUI controls
ANIMATION_INFO = {
    'name': 'Enhanced Cosmic Nebulas',
    'description': 'Six distinct nebula formations with dramatic contrasts and seamless transitions',
    'author': 'CosmicLED Enhanced',
    'version': '2.0',
    'parameters': {
        'speed': 'Animation speed (0.1-3.0, recommended: 0.5-1.5)',
        'scale': 'Nebula size scale (0.5-2.0, recommended: 0.8-1.2)', 
        'hue_offset': 'Color shift for all nebulas (0-360 degrees)',
        'saturation': 'Color saturation intensity (0.0-1.0, recommended: 0.8-1.0)',
        'brightness': 'Overall brightness (0.0-1.0, recommended: 0.3-0.8)',
        'gamma': 'Gamma correction for color accuracy (0.5-3.0, recommended: 1.8-2.2)'
    },
    'features': [
        '6 distinct nebula shapes: circular, spiral, ring, cloud, asymmetric, binary',
        '2-minute seamless transitions between formations',
        'High-resolution core rendering with 4x4 subpixel sampling',
        'Dramatic color contrasts with black feathering between layers',
        'Subtle breathing effects without individual pixel flashing',
        'Shape-specific transformations and organic turbulence',
        'Enhanced saturation for vivid, non-washed out cores'
    ],
    'cycle_info': {
        'transition_duration': '2 minutes continuous',
        'hold_duration': 'None - continuous transitions',
        'total_cycle': '2 minutes per nebula',
        'total_sequence': '12 minutes for all 6 nebulas'
    }
}

def apply_shape_transform(nx, ny, center_x, center_y, base_distance, shape, spiral_arms, frame, config):
    """
    Apply shape-specific transformations to create varied nebula forms
    """
    dx = nx - center_x
    dy = ny - center_y
    
    if shape == 'circular':
        return base_distance
    
    elif shape == 'spiral':
        # Create spiral arms
        angle = math.atan2(dy, dx)
        spiral_offset = math.sin(angle * spiral_arms + base_distance * 8.0 + frame * config.speed * 0.01) * 0.1
        return base_distance + spiral_offset
    
    elif shape == 'ring':
        # Create ring structure with hollow center
        ring_center = 0.25  # Distance from center where ring is strongest
        ring_falloff = abs(base_distance - ring_center) * 2.0
        return ring_falloff
    
    elif shape == 'cloud':
        # Irregular cloud-like formations
        cloud_noise = (math.sin(nx * 6.0 + frame * 0.002) * math.cos(ny * 8.0 + frame * 0.0015) + 
                      math.sin(nx * 12.0 + frame * 0.001) * math.cos(ny * 4.0 + frame * 0.003)) * 0.15
        return base_distance + cloud_noise
    
    elif shape == 'asymmetric':
        # Asymmetric distortion simulating gravitational effects
        asymmetry = math.sin(math.atan2(dy, dx) * 2.0 + frame * config.speed * 0.005) * 0.2
        return base_distance * (1.0 + asymmetry)
    
    elif shape == 'binary':
        # Binary core system
        core1_dx = dx + 0.1
        core1_dy = dy
        core2_dx = dx - 0.1
        core2_dy = dy
        
        dist1 = math.sqrt(core1_dx * core1_dx + core1_dy * core1_dy)
        dist2 = math.sqrt(core2_dx * core2_dx + core2_dy * core2_dy)
        
        return min(dist1, dist2)  # Distance to nearest core
    
    else:
        return base_distance

def calculate_nebula_color(nx, ny, current_config, next_config, blend_factor, frame, config):
    """
    Calculate the color for a single point in the nebula
    """
    final_r, final_g, final_b = 0, 0, 0
    
    for nebula_weight, nebula_config in [(1.0 - blend_factor, current_config), (blend_factor, next_config)]:
        if nebula_weight < 0.01:
            continue
            
        center_x, center_y = nebula_config['center']
        core_size = nebula_config['core_size'] * config.scale
        outer_size = nebula_config['outer_size'] * config.scale
        colors = nebula_config['colors']
        turbulence = nebula_config['turbulence']
        shape = nebula_config['shape']
        spiral_arms = nebula_config.get('spiral_arms', 0)
        
        # Calculate base distance from nebula center
        dx = nx - center_x
        dy = ny - center_y
        base_distance = math.sqrt(dx * dx + dy * dy)
        
        # Apply shape-specific modifications
        distance = apply_shape_transform(nx, ny, center_x, center_y, base_distance, shape, spiral_arms, frame, config)
        
        # Skip if too far from nebula
        if distance > outer_size:
            continue
        
        # Static distance only - no turbulence to prevent pixel flickering
        turbulent_distance = distance
        
        # Define three distinct zones with different size thresholds
        middle_size = core_size * 2.2  # Middle zone extends beyond core
        
        # Universal breathing effect - very gentle, never goes below 80% to prevent pixels turning off
        universal_breath = 0.9 + 0.1 * math.sin(frame * config.speed * 0.004)  # Gentler breathing (80%-100%)
        
        # Zone calculations with black feathering between layers
        core_intensity = 0.0
        middle_intensity = 0.0
        outer_intensity = 0.0
        current_zone = 'none'
        
        # Define transition zones for black feathering
        core_transition = core_size * 1.05  # 5% buffer around core
        middle_transition = middle_size * 1.08  # 8% buffer around middle
        
        # Zone 1: Ultra-small deeply saturated core (extremely sharp falloff) - static with universal breathing only
        if turbulent_distance < core_size:
            core_intensity = math.exp(-turbulent_distance * 25.0 / core_size)  # Much sharper falloff for tiny cores
            core_intensity *= universal_breath  # Only universal breathing, no individual modulation
            current_zone = 'core'
        
        # Black feathering zone 1: Between core and middle (static feathering)
        elif turbulent_distance >= core_size and turbulent_distance < core_transition:
            # Create black separation with static feathering pattern
            feather_progress = (turbulent_distance - core_size) / (core_transition - core_size)
            feather_noise = 0.3 * math.sin(nx * 20.0) * math.cos(ny * 18.0)  # Static pattern
            feather_cutoff = 0.7 + 0.3 * feather_noise  # Static irregular feathering
            
            if feather_progress > feather_cutoff:
                core_intensity = 0.0
                current_zone = 'separation'
            else:
                # Fade out core at edge
                core_intensity = math.exp(-turbulent_distance * 25.0 / core_size) * (1.0 - feather_progress)
                core_intensity *= universal_breath  # Only universal breathing
                current_zone = 'core'
        
        # Zone 2: Middle transition area (medium saturation, gradual falloff) - more static
        elif turbulent_distance >= core_transition and turbulent_distance < middle_size:
            middle_distance_norm = (turbulent_distance - core_transition) / (middle_size - core_transition)
            middle_intensity = math.exp(-middle_distance_norm * 4.0) * (1.0 - middle_distance_norm * 0.7)
            
            # Static structure with minimal noise, only universal breathing
            middle_intensity *= universal_breath
            current_zone = 'middle'
        
        # Black feathering zone 2: Between middle and outer (static feathering)
        elif turbulent_distance >= middle_size and turbulent_distance < middle_transition:
            # Create black separation with static feathering pattern
            feather_progress = (turbulent_distance - middle_size) / (middle_transition - middle_size)
            feather_noise = 0.4 * math.sin(nx * 25.0) * math.cos(ny * 22.0)  # Static pattern
            feather_cutoff = 0.6 + 0.4 * feather_noise  # Static irregular outer feathering
            
            if feather_progress > feather_cutoff:
                middle_intensity = 0.0
                current_zone = 'separation'
            else:
                # Fade out middle at edge
                middle_distance_norm = (middle_size - core_transition) / (middle_size - core_transition)
                middle_intensity = math.exp(-middle_distance_norm * 4.0) * (1.0 - feather_progress)
                middle_intensity *= universal_breath  # Only universal breathing
                current_zone = 'middle'
        
        # Zone 3: Outer wispy area (low saturation, very gradual fade to empty space) - more static
        elif turbulent_distance >= middle_transition and turbulent_distance < outer_size:
            outer_distance_norm = (turbulent_distance - middle_transition) / (outer_size - middle_transition)
            outer_intensity = math.exp(-outer_distance_norm * 2.5) * (1.0 - outer_distance_norm * 0.9)
            
            # Static outer zone with only universal breathing
            outer_intensity *= universal_breath * 0.8  # Slightly reduced for outer zone
            current_zone = 'outer'
        
        # Combine intensities with zone priorities - boost tiny cores significantly
        if core_intensity > 0.01:  # Small threshold to prevent flashing
            total_intensity = max(0.1, core_intensity * 0.9)  # Much brighter for tiny cores - minimum 10% brightness
        elif middle_intensity > 0.01:
            total_intensity = max(0.03, middle_intensity * 0.8)  # Minimum 3% brightness
        elif outer_intensity > 0.01:
            total_intensity = max(0.02, outer_intensity * 0.3)  # Minimum 2% brightness
        else:
            total_intensity = 0.0
        
        # Apply flash effect to core (keep from original)
        flash_intensity = 0.0
        in_transition = True  # This should be passed as parameter, simplified for now
        transition_progress = 0.5  # This should be calculated, simplified for now
        
        if total_intensity > 0.01:
            # Enhanced color selection with dramatic contrasts (static)
            if current_zone == 'core':
                hue, sat, val = colors[0]
                sat = 1.0  # Maximum saturation
                val = min(1.0, val * 0.6)  # Reduce brightness to avoid washout
                # Static core variation based on position only
                core_variation = 0.05 * math.sin(base_distance * 10.0)
                hue = (hue + core_variation * 10) % 360
                
            elif current_zone == 'middle':
                middle_t = (turbulent_distance - core_size) / (middle_size - core_size)
                hue = colors[0][0] * (1-middle_t) + colors[1][0] * middle_t
                sat = (colors[0][1] * (1-middle_t) + colors[1][1] * middle_t) * 0.9
                val = (colors[0][2] * (1-middle_t) + colors[1][2] * middle_t) * 1.1
                # Static color variation based on position only
                color_turbulence = 0.1 * math.sin(nx * 10.0) * math.cos(ny * 8.0)
                hue = (hue + color_turbulence * 15) % 360
                
            elif current_zone == 'outer':
                outer_t = (turbulent_distance - middle_size) / (outer_size - middle_size)
                hue = colors[1][0] * (1-outer_t) + colors[2][0] * outer_t
                sat = (colors[1][1] * (1-outer_t) + colors[2][1] * outer_t) * 0.6
                val = (colors[1][2] * (1-outer_t) + colors[2][2] * outer_t) * 0.8
                # Static outer variation based on position only
                wispy_variation = 0.08 * math.sin(nx * 20.0) * math.cos(ny * 16.0)
                hue = (hue + wispy_variation * 20) % 360
            else:
                hue, sat, val = colors[0]
            
            # Apply hue offset
            hue = (hue + config.hue_offset) % 360
            
            # Apply intensity and configuration
            final_sat = sat * config.saturation
            final_val = val * total_intensity * config.brightness * nebula_weight
            
            # Convert to RGB and add to final color
            r, g, b = colorsys.hsv_to_rgb(hue / 360.0, final_sat, final_val)
            final_r += r
            final_g += g
            final_b += b
    
    return final_r, final_g, final_b

def animate(pixels, config, frame):
    """
    Static cosmic nebula animation with universal breathing and seamless transitions
    
    Features:
    - Static nebula formations with only universal breathing (no individual movement)
    - Small, high-resolution cores with 8x8 subpixel sampling
    - Seamless 2-minute transitions between 6 distinct nebulas
    - Continuous cycling with no hold periods
    
    Timing:
    - 2 minutes continuous transition between each nebula
    - 12 minute total cycle for all 6 nebulas
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Timing constants - 2 minute seamless transitions (assumes 15 FPS)
    fps = getattr(config, 'fps', 15)  # Default to 15 FPS if not specified
    transition_duration = 120 * fps  # Exactly 2 minutes in frames  
    hold_duration = 0 * fps          # No hold time - continuous transitions
    total_cycle = transition_duration + hold_duration  # 2 minute cycles
    
    # Current position in cycle
    cycle_frame = frame % total_cycle
    
    # Always in transition since there's no hold phase
    in_transition = True
    transition_progress = cycle_frame / transition_duration
    
    # Calculate which nebulas we're working with
    nebula_index = int(frame / total_cycle)
    current_nebula = nebula_index % 6
    next_nebula = (nebula_index + 1) % 6
    
    # Ultra-small, high-resolution cores (approximately 1 LED size each)
    nebula_configs = [
        {
            'center': (0.5, 0.5),
            'shape': 'circular',
            'core_size': 0.025,  # Tiny core (~1 LED on 10x10 matrix)
            'outer_size': 0.45,
            'colors': [(15, 1.0, 1.0), (35, 0.9, 0.8), (200, 0.6, 0.4)],  # Intense red-orange → Deep blue (dramatic contrast)
            'turbulence': 0.4,  # Reduced turbulence for more static appearance
            'spiral_arms': 0,
            'name': 'Crimson-Void Nebula'
        },
        {
            'center': (0.4, 0.6),
            'shape': 'spiral',
            'core_size': 0.02,  # Tiny core
            'outer_size': 0.5,
            'colors': [(240, 1.0, 1.0), (260, 0.8, 0.9), (50, 0.4, 0.5)],  # Brilliant blue → Deep purple → Golden outer
            'turbulence': 0.3,  # Reduced turbulence
            'spiral_arms': 3,
            'name': 'Sapphire Spiral Nebula'
        },
        {
            'center': (0.6, 0.4),
            'shape': 'ring',
            'core_size': 0.015,  # Tiny core
            'outer_size': 0.48,
            'colors': [(300, 1.0, 1.0), (320, 0.7, 0.8), (120, 0.5, 0.6)],  # Vivid magenta → Soft pink → Emerald ring
            'turbulence': 0.5,  # Reduced turbulence
            'spiral_arms': 0,
            'name': 'Orchid Ring Nebula'
        },
        {
            'center': (0.5, 0.3),
            'shape': 'cloud',
            'core_size': 0.03,  # Tiny core
            'outer_size': 0.55,
            'colors': [(120, 1.0, 1.0), (80, 0.9, 0.9), (270, 0.3, 0.7)],  # Brilliant green → Lime → Deep violet clouds
            'turbulence': 0.6,  # Reduced turbulence
            'spiral_arms': 0,
            'name': 'Emerald Cloud Nebula'
        },
        {
            'center': (0.3, 0.7),
            'shape': 'asymmetric',
            'core_size': 0.022,  # Tiny core
            'outer_size': 0.52,
            'colors': [(180, 1.0, 1.0), (160, 0.8, 0.9), (30, 0.4, 0.6)],  # Cyan → Teal → Amber asymmetric
            'turbulence': 0.4,  # Reduced turbulence
            'spiral_arms': 2,
            'name': 'Tidal Force Nebula'
        },
        {
            'center': (0.7, 0.3),
            'shape': 'binary',
            'core_size': 0.018,  # Tiny core
            'outer_size': 0.43,
            'colors': [(0, 1.0, 1.0), (20, 0.9, 0.8), (240, 0.5, 0.5)],  # Pure red → Orange → Blue binary cores
            'turbulence': 0.35,  # Reduced turbulence
            'spiral_arms': 0,
            'name': 'Binary Core Nebula'
        }
    ]
    
    current_config = nebula_configs[current_nebula]
    next_config = nebula_configs[next_nebula] if in_transition else current_config
    
    # Flash timing - two bright flashes at start of transition
    flash_intensity = 0.0
    if in_transition and transition_progress < 0.05:  # First 3 seconds
        flash_time = transition_progress / 0.05
        if flash_time < 0.5:
            # First flash
            flash_intensity = math.sin(flash_time * math.pi * 4) * 0.8
        elif flash_time < 1.0:
            # Second flash  
            flash_intensity = math.sin((flash_time - 0.5) * math.pi * 4) * 0.6
    
    # Smooth transition interpolation (ease in-out)
    if in_transition:
        t = transition_progress
        # Ease-in-out curve
        blend_factor = 3 * t * t - 2 * t * t * t
    else:
        blend_factor = 0.0
    
    total_pixels = config.matrix_width * config.matrix_height
    
    # Ultra-high-resolution core sampling parameters - maximum detail for tiny cores
    core_resolution_multiplier = 16  # 16x16 subpixel sampling for cores (256 samples per pixel)
    
    for i in range(total_pixels):
        # Get pixel coordinates
        x = i % config.matrix_width
        y = i // config.matrix_width
        
        # Normalize coordinates (0.0 to 1.0)
        nx = x / (config.matrix_width - 1)
        ny = y / (config.matrix_height - 1)
        
        # Check if we're near any nebula core for high-resolution sampling
        use_high_res = False
        for nebula_config in [current_config, next_config]:
            center_x, center_y = nebula_config['center']
            core_size = nebula_config['core_size'] * config.scale
            dx = nx - center_x
            dy = ny - center_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < core_size * 4.0:  # High-res sampling within 4x core radius for tiny cores
                use_high_res = True
                break
        
        # Calculate final pixel color using high-resolution sampling if needed
        if use_high_res:
            # High-resolution subpixel sampling for cores
            sample_r, sample_g, sample_b = 0, 0, 0
            samples = core_resolution_multiplier * core_resolution_multiplier
            
            for sub_x in range(core_resolution_multiplier):
                for sub_y in range(core_resolution_multiplier):
                    # Calculate subpixel position
                    offset_x = (sub_x + 0.5) / core_resolution_multiplier - 0.5
                    offset_y = (sub_y + 0.5) / core_resolution_multiplier - 0.5
                    
                    sub_nx = nx + offset_x / (config.matrix_width - 1)
                    sub_ny = ny + offset_y / (config.matrix_height - 1)
                    
                    # Calculate nebula color for this subpixel
                    sub_r, sub_g, sub_b = calculate_nebula_color(sub_nx, sub_ny, current_config, next_config, 
                                                               blend_factor, frame, config)
                    
                    sample_r += sub_r
                    sample_g += sub_g
                    sample_b += sub_b
            
            # Average the samples
            final_r = sample_r / samples
            final_g = sample_g / samples
            final_b = sample_b / samples
        else:
            # Standard resolution sampling
            final_r, final_g, final_b = calculate_nebula_color(nx, ny, current_config, next_config, 
                                                             blend_factor, frame, config)
        
        # Apply gamma correction
        gamma = config.gamma
        final_r = math.pow(max(0, min(1, final_r)), 1.0 / gamma)
        final_g = math.pow(max(0, min(1, final_g)), 1.0 / gamma)
        final_b = math.pow(max(0, min(1, final_b)), 1.0 / gamma)
        
        # No star field to prevent flickering - keep space purely dark
        
        # Convert to 0-255 range
        r = int(max(0, min(255, final_r * 255)))
        g = int(max(0, min(255, final_g * 255)))
        b = int(max(0, min(255, final_b * 255)))
        
        pixels[i] = (r, g, b)