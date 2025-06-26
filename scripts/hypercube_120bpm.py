#!/usr/bin/env python3
"""
Hypercube 120 BPM Animation
A 4D hypercube projected to 2D that morphs and pulses in sync with 120 BPM
Features rotating projections, beat-synchronized morphing, and musical phrasing
"""

import math
import colorsys
import time

ANIMATION_INFO = {
    'name': 'Hypercube 120 BPM',
    'description': 'A 4D hypercube projection that morphs and pulses to synthesized 120 BPM timing',
    'version': '1.0',
    'author': 'Claude Code',
    'parameters': {
        'speed': 'Controls rotation speed of the hypercube (0.1-2.0)',
        'scale': 'Size of the hypercube projection (0.5-2.0)',
        'brightness': 'Overall brightness (0.1-1.0)'
    },
    'features': [
        '4D to 2D hypercube projection',
        '120 BPM beat synchronization',
        'Musical phrase-based morphing',
        'Dynamic color transitions',
        'Beat-responsive pulsing'
    ],
    'cycle_info': {
        'beat_interval': '0.5 seconds (120 BPM)',
        'phrase_length': '8 beats (4 seconds)',
        'full_cycle': '32 beats (16 seconds)'
    }
}

class Hypercube4D:
    """4D Hypercube (Tesseract) with projection and animation capabilities"""
    
    def __init__(self):
        # 4D hypercube vertices (16 vertices in 4D space)
        self.vertices_4d = []
        for i in range(16):
            x = 1 if i & 1 else -1
            y = 1 if i & 2 else -1
            z = 1 if i & 4 else -1
            w = 1 if i & 8 else -1
            self.vertices_4d.append([x, y, z, w])
        
        # Hypercube edges (connecting vertices)
        self.edges = []
        for i in range(16):
            for j in range(i + 1, 16):
                # Two vertices are connected if they differ in exactly one coordinate
                diff_count = sum(1 for k in range(4) if self.vertices_4d[i][k] != self.vertices_4d[j][k])
                if diff_count == 1:
                    self.edges.append((i, j))
        
        # Beat timing for 120 BPM
        self.bpm = 120
        self.beat_duration = 60.0 / self.bpm  # 0.5 seconds per beat
        self.phrase_length = 8  # beats per phrase
        self.phrase_duration = self.beat_duration * self.phrase_length  # 4 seconds
        
    def rotate_4d(self, vertices, angle_xy, angle_xz, angle_xw, angle_yz, angle_yw, angle_zw):
        """Apply 4D rotations to vertices"""
        rotated = []
        
        for vertex in vertices:
            x, y, z, w = vertex
            
            # XY rotation
            cos_xy, sin_xy = math.cos(angle_xy), math.sin(angle_xy)
            x, y = x * cos_xy - y * sin_xy, x * sin_xy + y * cos_xy
            
            # XZ rotation  
            cos_xz, sin_xz = math.cos(angle_xz), math.sin(angle_xz)
            x, z = x * cos_xz - z * sin_xz, x * sin_xz + z * cos_xz
            
            # XW rotation
            cos_xw, sin_xw = math.cos(angle_xw), math.sin(angle_xw)
            x, w = x * cos_xw - w * sin_xw, x * sin_xw + w * cos_xw
            
            # YZ rotation
            cos_yz, sin_yz = math.cos(angle_yz), math.sin(angle_yz)
            y, z = y * cos_yz - z * sin_yz, y * sin_yz + z * cos_yz
            
            # YW rotation
            cos_yw, sin_yw = math.cos(angle_yw), math.sin(angle_yw)
            y, w = y * cos_yw - w * sin_yw, y * sin_yw + w * cos_yw
            
            # ZW rotation
            cos_zw, sin_zw = math.cos(angle_zw), math.sin(angle_zw)
            z, w = z * cos_zw - w * sin_zw, z * sin_zw + w * cos_zw
            
            rotated.append([x, y, z, w])
        
        return rotated
    
    def project_to_2d(self, vertices_4d, scale=2.0):
        """Project 4D vertices to 2D screen coordinates"""
        vertices_2d = []
        
        for vertex in vertices_4d:
            x, y, z, w = vertex
            
            # Safer 4D to 3D projection
            distance_4d = 4.0
            w_factor = max(0.1, distance_4d + w * 0.5)  # Prevent division by zero
            scale_3d = distance_4d / w_factor
            x3d = x * scale_3d
            y3d = y * scale_3d
            z3d = z * scale_3d
            
            # Safer 3D to 2D projection
            distance_3d = 4.0
            z_factor = max(0.1, distance_3d + z3d * 0.5)  # Prevent division by zero
            scale_2d = distance_3d / z_factor
            x2d = x3d * scale_2d * scale * 0.3  # Scale down to fit matrix
            y2d = y3d * scale_2d * scale * 0.3
            
            vertices_2d.append([x2d, y2d])
        
        return vertices_2d

def get_beat_info(frame, fps=15):
    """Calculate current beat and phrase information"""
    time_elapsed = frame / fps
    beat_duration = 60.0 / 120  # 120 BPM = 0.5 seconds per beat
    phrase_duration = beat_duration * 8  # 8 beats per phrase
    
    current_beat = (time_elapsed / beat_duration) % 8
    current_phrase = int(time_elapsed / phrase_duration) % 4
    beat_progress = (time_elapsed % beat_duration) / beat_duration
    phrase_progress = (time_elapsed % phrase_duration) / phrase_duration
    
    return {
        'beat': current_beat,
        'phrase': current_phrase,
        'beat_progress': beat_progress,
        'phrase_progress': phrase_progress,
        'is_beat': beat_progress < 0.2,  # Beat pulse for first 20% of beat
        'time': time_elapsed
    }

def get_beat_intensity(beat_info):
    """Calculate beat-based intensity multiplier"""
    if beat_info['is_beat']:
        # Strong pulse on beat
        return 1.0 + 0.5 * (1.0 - beat_info['beat_progress'] / 0.2)
    else:
        # Gentle breathing between beats
        phase = (beat_info['beat_progress'] - 0.2) / 0.8
        return 1.0 + 0.1 * math.sin(phase * math.pi * 2)

def draw_line(pixels, config, x1, y1, x2, y2, color, intensity=1.0):
    """Draw a line between two points with anti-aliasing"""
    # Convert from [-1,1] range to pixel coordinates
    px1 = int((x1 + 1) * config.matrix_width / 2)
    py1 = int((y1 + 1) * config.matrix_height / 2)
    px2 = int((x2 + 1) * config.matrix_width / 2)
    py2 = int((y2 + 1) * config.matrix_height / 2)
    
    # Simple line drawing with interpolation
    dx = abs(px2 - px1)
    dy = abs(py2 - py1)
    steps = max(dx, dy, 1)
    
    for i in range(steps + 1):
        t = i / steps if steps > 0 else 0
        px = int(px1 + t * (px2 - px1))
        py = int(py1 + t * (py2 - py1))
        
        if 0 <= px < config.matrix_width and 0 <= py < config.matrix_height:
            index = config.xy_to_index(px, py)
            if 0 <= index < len(pixels):
                # Apply intensity and blend with existing color
                r, g, b = color
                
                # Clamp values to valid range
                r = max(0, min(255, int(r * intensity * config.brightness)))
                g = max(0, min(255, int(g * intensity * config.brightness)))
                b = max(0, min(255, int(b * intensity * config.brightness)))
                
                # Get existing color and blend
                try:
                    existing = pixels[index]
                    if isinstance(existing, (tuple, list)) and len(existing) >= 3:
                        r = min(255, r + existing[0] // 4)
                        g = min(255, g + existing[1] // 4)
                        b = min(255, b + existing[2] // 4)
                except:
                    pass
                
                # Apply color correction
                if hasattr(config, 'correct_color'):
                    r, g, b = config.correct_color(r, g, b)
                pixels[index] = (r, g, b)

def animate(pixels, config, frame):
    """Main animation function"""
    try:
        # Clear the display
        for i in range(len(pixels)):
            pixels[i] = (0, 0, 0)
        
        # Initialize hypercube
        hypercube = Hypercube4D()
        
        # Get beat timing information
        beat_info = get_beat_info(frame, fps=config.fps)
        beat_intensity = get_beat_intensity(beat_info)
        
        # Calculate rotation angles based on time and beat (slower rotation)
        time_factor = frame * config.speed * 0.005  # Reduced speed
        beat_factor = beat_info['beat_progress'] * 0.1
        phrase_factor = beat_info['phrase_progress'] * 0.05
        
        # Different rotation speeds for each plane (reduced)
        angle_xy = time_factor * 0.3 + beat_factor
        angle_xz = time_factor * 0.2 + phrase_factor
        angle_xw = time_factor * 0.15 + beat_info['phrase'] * 0.05
        angle_yz = time_factor * 0.25 + beat_factor * 0.3
        angle_yw = time_factor * 0.18 + phrase_factor * 0.4
        angle_zw = time_factor * 0.35 + beat_info['beat'] * 0.02
        
        # Apply beat-synchronized morphing (reduced)
        morph_factor = 1.0 + 0.1 * math.sin(beat_info['phrase_progress'] * math.pi * 2)
        
        # Rotate the hypercube
        rotated_vertices = hypercube.rotate_4d(
            hypercube.vertices_4d, 
            angle_xy, angle_xz, angle_xw, 
            angle_yz, angle_yw, angle_zw
        )
        
        # Project to 2D (smaller scale)
        scale = min(3.0, config.scale * morph_factor * beat_intensity * 0.5)
        projected_vertices = hypercube.project_to_2d(rotated_vertices, scale)
        
        # Color palette based on musical phrase
        phrase_colors = [
            (255, 80, 80),   # Red phase
            (80, 255, 80),   # Green phase  
            (80, 80, 255),   # Blue phase
            (255, 255, 80),  # Yellow phase
        ]
        
        base_color = phrase_colors[int(beat_info['phrase']) % 4]
        
        # Draw the hypercube edges (limit number for performance)
        edges_to_draw = hypercube.edges[:16]  # Draw first 16 edges only
        for edge_idx, (v1_idx, v2_idx) in enumerate(edges_to_draw):
            if v1_idx < len(projected_vertices) and v2_idx < len(projected_vertices):
                v1 = projected_vertices[v1_idx]
                v2 = projected_vertices[v2_idx]
                
                # Skip edges that are too far from center
                if abs(v1[0]) > 2 or abs(v1[1]) > 2 or abs(v2[0]) > 2 or abs(v2[1]) > 2:
                    continue
                
                # Simple color variation
                color_factor = (edge_idx * 0.1 + beat_info['beat_progress']) % 1.0
                r, g, b = base_color
                r = max(20, int(r * (0.5 + 0.5 * color_factor)))
                g = max(20, int(g * (0.5 + 0.5 * color_factor)))
                b = max(20, int(b * (0.5 + 0.5 * color_factor)))
                color = (r, g, b)
                
                # Draw line with consistent intensity
                edge_intensity = 0.8 * beat_intensity
                draw_line(pixels, config, v1[0], v1[1], v2[0], v2[1], color, edge_intensity)
        
        # Add beat-synchronized center pulse
        if beat_info['is_beat']:
            center_x = config.matrix_width // 2
            center_y = config.matrix_height // 2
            
            if 0 <= center_x < config.matrix_width and 0 <= center_y < config.matrix_height:
                index = config.xy_to_index(center_x, center_y)
                if 0 <= index < len(pixels):
                    intensity = beat_intensity * 0.5
                    r, g, b = base_color
                    r_final = min(255, int(r * intensity))
                    g_final = min(255, int(g * intensity))
                    b_final = min(255, int(b * intensity))
                    
                    # Apply color correction
                    if hasattr(config, 'correct_color'):
                        r_final, g_final, b_final = config.correct_color(r_final, g_final, b_final)
                    
                    pixels[index] = (r_final, g_final, b_final)
    
    except Exception as e:
        # Fallback: simple pulsing pattern if hypercube fails
        center_x = config.matrix_width // 2
        center_y = config.matrix_height // 2
        
        beat_time = (frame / config.fps) / 0.5
        pulse = 0.5 + 0.5 * math.sin(beat_time * math.pi * 2)
        
        for y in range(config.matrix_height):
            for x in range(config.matrix_width):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                if dist < 3:
                    index = config.xy_to_index(x, y)
                    if 0 <= index < len(pixels):
                        intensity = (1.0 - dist / 3) * pulse
                        r_final = int(255 * intensity)
                        g_final = int(100 * intensity)
                        b_final = int(100 * intensity)
                        
                        # Apply color correction
                        if hasattr(config, 'correct_color'):
                            r_final, g_final, b_final = config.correct_color(r_final, g_final, b_final)
                        
                        pixels[index] = (r_final, g_final, b_final)