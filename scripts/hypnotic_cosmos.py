"""
Hypnotic Cosmos - The Most Dynamic Visual Experience
Combines plasma fields, rotating galaxies, particle explosions, color waves,
lightning bolts, ripple effects, and morphing geometric patterns
"""

import math
import random
from typing import List, Tuple

class VisualLayer:
    """Base class for visual effect layers"""
    def __init__(self):
        self.intensity = 1.0
        
    def render(self, x, y, frame, config):
        return (0, 0, 0)

class PlasmaField(VisualLayer):
    """Animated plasma field with multiple frequencies"""
    def render(self, x, y, frame, config):
        speed = getattr(config, 'speed', 1.0)
        scale = getattr(config, 'scale', 1.0)
        
        time = frame * speed * 0.1
        
        # Multiple plasma waves
        plasma1 = math.sin(x * 0.5 / scale + time)
        plasma2 = math.cos(y * 0.7 / scale + time * 1.3)
        plasma3 = math.sin((x + y) * 0.3 / scale + time * 0.8)
        plasma4 = math.cos((x - y) * 0.4 / scale + time * 1.7)
        
        # Combine plasma fields
        intensity = (plasma1 + plasma2 + plasma3 + plasma4) / 4.0
        intensity = (intensity + 1.0) / 2.0  # Normalize 0-1
        
        # Rainbow colors based on position and time
        hue = (intensity + time * 0.5 + x * 0.1 + y * 0.1) % 1.0
        return hsv_to_rgb(hue, 0.8, intensity)

class GalaxySpiral(VisualLayer):
    """Rotating galaxy with spiral arms"""
    def render(self, x, y, frame, config):
        width = getattr(config, 'matrix_width', 10)
        height = getattr(config, 'matrix_height', 10)
        speed = getattr(config, 'speed', 1.0)
        
        # Center coordinates
        cx, cy = width / 2, height / 2
        
        # Distance from center
        dx, dy = x - cx, y - cy
        distance = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)
        
        # Rotating spiral
        time = frame * speed * 0.05
        spiral_angle = angle + distance * 0.5 - time * 2.0
        
        # Spiral intensity
        spiral_intensity = math.sin(spiral_angle * 3.0) * 0.5 + 0.5
        
        # Distance falloff
        falloff = max(0, 1.0 - distance / (max(width, height) * 0.7))
        
        intensity = spiral_intensity * falloff
        
        # Purple/blue galaxy colors
        hue = 0.7 + math.sin(time + distance * 0.2) * 0.1
        return hsv_to_rgb(hue, 0.9, intensity)

class ParticleExplosion(VisualLayer):
    """Explosive particle bursts"""
    def __init__(self):
        super().__init__()
        self.explosions = []
        
    def render(self, x, y, frame, config):
        width = getattr(config, 'matrix_width', 10)
        height = getattr(config, 'matrix_height', 10)
        speed = getattr(config, 'speed', 1.0)
        
        # Create new explosions randomly
        if random.random() < 0.02 * speed:
            self.explosions.append({
                'x': random.uniform(0, width),
                'y': random.uniform(0, height),
                'start_frame': frame,
                'color': random.choice([
                    (1.0, 0.3, 0.0),  # Orange
                    (1.0, 0.0, 0.3),  # Red
                    (0.0, 0.5, 1.0),  # Blue
                    (1.0, 1.0, 0.0),  # Yellow
                    (0.5, 0.0, 1.0),  # Purple
                ])
            })
        
        # Remove old explosions
        self.explosions = [e for e in self.explosions if frame - e['start_frame'] < 60]
        
        total_intensity = 0.0
        final_color = [0, 0, 0]
        
        # Render all explosions
        for explosion in self.explosions:
            age = frame - explosion['start_frame']
            max_age = 60
            
            # Distance from explosion center
            dx = x - explosion['x']
            dy = y - explosion['y']
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Expanding ring effect
            ring_radius = age * 0.2 * speed
            ring_width = 1.5
            
            if abs(distance - ring_radius) < ring_width:
                # Intensity based on ring proximity
                ring_intensity = 1.0 - abs(distance - ring_radius) / ring_width
                
                # Fade over time
                time_fade = 1.0 - (age / max_age)
                
                intensity = ring_intensity * time_fade
                
                if intensity > total_intensity:
                    total_intensity = intensity
                    final_color = [c * intensity for c in explosion['color']]
        
        return tuple(int(c * 255) for c in final_color)

class LightningBolt(VisualLayer):
    """Dynamic lightning bolts"""
    def render(self, x, y, frame, config):
        speed = getattr(config, 'speed', 1.0)
        
        # Lightning frequency
        time = frame * speed * 0.3
        
        # Random lightning strikes
        lightning_seed = int(time * 2) % 1000
        random.seed(lightning_seed)
        
        if random.random() > 0.95:  # 5% chance
            # Jagged lightning path
            lightning_y = random.uniform(0, getattr(config, 'matrix_height', 10))
            
            # Distance from lightning path
            distance = abs(y - lightning_y)
            
            # Lightning intensity with jagged edges
            jagged_offset = math.sin(x * 3.0 + time * 10) * 0.5
            distance += abs(jagged_offset)
            
            if distance < 1.5:
                intensity = 1.0 - (distance / 1.5)
                # Bright white/blue lightning
                return (int(255 * intensity), int(255 * intensity), int(255 * intensity))
        
        return (0, 0, 0)

class ColorWave(VisualLayer):
    """Flowing color waves"""
    def render(self, x, y, frame, config):
        speed = getattr(config, 'speed', 1.0)
        scale = getattr(config, 'scale', 1.0)
        
        time = frame * speed * 0.08
        
        # Multiple wave patterns
        wave1 = math.sin(x * 0.8 / scale + time * 2.0)
        wave2 = math.cos(y * 0.6 / scale + time * 1.5)
        wave3 = math.sin((x + y) * 0.4 / scale + time * 2.5)
        
        # Combine waves
        combined = (wave1 + wave2 + wave3) / 3.0
        intensity = (combined + 1.0) / 2.0
        
        # Shifting rainbow colors
        hue = (time * 0.3 + x * 0.05 + y * 0.05) % 1.0
        
        return hsv_to_rgb(hue, 1.0, intensity)

class GeometricMorph(VisualLayer):
    """Morphing geometric patterns"""
    def render(self, x, y, frame, config):
        width = getattr(config, 'matrix_width', 10)
        height = getattr(config, 'matrix_height', 10)
        speed = getattr(config, 'speed', 1.0)
        
        cx, cy = width / 2, height / 2
        dx, dy = x - cx, y - cy
        
        time = frame * speed * 0.1
        
        # Rotating geometric shapes
        angle = math.atan2(dy, dx) + time
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Multiple geometric patterns
        pattern1 = math.sin(angle * 6.0 + time) * 0.5 + 0.5  # Hexagon
        pattern2 = math.sin(angle * 4.0 - time * 1.3) * 0.5 + 0.5  # Square
        pattern3 = math.sin(angle * 8.0 + time * 0.7) * 0.5 + 0.5  # Octagon
        
        # Morphing between patterns
        morph_time = math.sin(time * 0.5) * 0.5 + 0.5
        pattern = pattern1 * morph_time + pattern2 * (1 - morph_time)
        pattern = pattern * 0.7 + pattern3 * 0.3
        
        # Distance-based intensity
        max_distance = max(width, height) * 0.6
        distance_factor = max(0, 1.0 - distance / max_distance)
        
        intensity = pattern * distance_factor
        
        # Shifting colors
        hue = (time * 0.2 + angle * 0.1) % 1.0
        return hsv_to_rgb(hue, 0.7, intensity)

# Initialize effect layers
plasma = PlasmaField()
galaxy = GalaxySpiral()
particles = ParticleExplosion()
lightning = LightningBolt()
waves = ColorWave()
geometry = GeometricMorph()

def animate(pixels, config, frame):
    """
    Master animation function combining all dynamic effects
    """
    width = getattr(config, 'matrix_width', 10)
    height = getattr(config, 'matrix_height', 10)
    speed = getattr(config, 'speed', 1.0)
    
    # Dynamic layer mixing based on time
    time = frame * speed * 0.02
    
    # Layer weights that change over time
    plasma_weight = (math.sin(time * 0.7) * 0.5 + 0.5) * 0.4
    galaxy_weight = (math.cos(time * 0.5) * 0.5 + 0.5) * 0.3
    particle_weight = 0.6  # Always strong
    lightning_weight = 1.0  # Full intensity when active
    wave_weight = (math.sin(time * 1.2) * 0.5 + 0.5) * 0.5
    geometry_weight = (math.cos(time * 0.8) * 0.5 + 0.5) * 0.3
    
    for y in range(height):
        for x in range(width):
            # Get colors from all layers
            plasma_color = plasma.render(x, y, frame, config)
            galaxy_color = galaxy.render(x, y, frame, config)
            particle_color = particles.render(x, y, frame, config)
            lightning_color = lightning.render(x, y, frame, config)
            wave_color = waves.render(x, y, frame, config)
            geometry_color = geometry.render(x, y, frame, config)
            
            # Blend all layers with dynamic weights
            final_color = [0, 0, 0]
            
            # Add each layer with its weight
            layers = [
                (plasma_color, plasma_weight),
                (galaxy_color, galaxy_weight),
                (particle_color, particle_weight),
                (lightning_color, lightning_weight),
                (wave_color, wave_weight),
                (geometry_color, geometry_weight)
            ]
            
            for color, weight in layers:
                for i in range(3):
                    final_color[i] += color[i] * weight
                    # Clamp intermediate values to prevent overflow
                    final_color[i] = min(255, max(0, final_color[i]))
            
            # Apply brightness and gamma (fixed to prevent range overflow)
            brightness = getattr(config, 'brightness', 1.0)
            gamma = getattr(config, 'gamma', 2.2)
            
            # Ensure brightness is clamped
            brightness = max(0.0, min(1.0, brightness))
            
            # Apply gamma correction first, then brightness
            final_color = [
                min(255, max(0, int(pow(c / 255.0, 1/gamma) * 255 * brightness)))
                for c in final_color
            ]
            
            # Set pixel with final clamping
            pixel_index = config.xy_to_index(x, y)
            if pixel_index < len(pixels):
                pixels[pixel_index] = (
                    int(max(0, min(255, final_color[0]))),
                    int(max(0, min(255, final_color[1]))),
                    int(max(0, min(255, final_color[2])))
                )

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color space"""
    h = h % 1.0
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    
    return (int(r * 255), int(g * 255), int(b * 255))

# Animation metadata
ANIMATION_NAME = "Hypnotic Cosmos"
ANIMATION_DESCRIPTION = "Ultimate dynamic visual experience with plasma, galaxies, explosions, lightning, and morphing geometry"
ANIMATION_AUTHOR = "Claude"
ANIMATION_VERSION = "1.0"