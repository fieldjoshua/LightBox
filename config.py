"""
Configuration management for CosmicLED
Handles settings persistence, color palettes, and matrix coordinate mapping
"""

import json
import os
import colorsys
from pathlib import Path

class Config:
    def __init__(self):
        # Matrix hardware settings (Pi Zero W optimized)
        self.matrix_width = 10
        self.matrix_height = 10
        self.serpentine_wiring = True  # True for serpentine, False for progressive
        
        # Animation settings (Pi Zero W optimized)
        self.brightness = 0.5
        self.gamma = 2.2
        self.fps = 15  # Reduced for Pi Zero W performance
        self.current_program = "aurora"
        
        # Color settings
        self.hue_offset = 0
        self.saturation = 1.0
        self.current_palette = "rainbow"
        
        # Animation parameters
        self.speed = 1.0
        self.scale = 1.0
        self.blend_mode = "normal"
        
        # Web server settings
        self.web_port = 5001  # Default to 5001 to avoid conflicts with macOS Control Center
        
        # LED color order correction (common issue with WS2811 strips)
        self.color_order = "GRB"  # Change to "RGB" if colors are correct, "GRB" if red shows as green
        
        # Change detection for real-time updates
        self._last_modified = 0
        self._update_counter = 0
        
        # Color palettes
        self.palettes = {
            "rainbow": [
                (255, 0, 0),    # Red
                (255, 127, 0),  # Orange
                (255, 255, 0),  # Yellow
                (0, 255, 0),    # Green
                (0, 0, 255),    # Blue
                (75, 0, 130),   # Indigo
                (148, 0, 211)   # Violet
            ],
            "fire": [
                (255, 0, 0),    # Red
                (255, 69, 0),   # Orange Red
                (255, 140, 0),  # Dark Orange
                (255, 215, 0),  # Gold
                (255, 255, 0)   # Yellow
            ],
            "ocean": [
                (0, 0, 139),    # Dark Blue
                (0, 0, 255),    # Blue
                (0, 191, 255),  # Deep Sky Blue
                (0, 255, 255),  # Cyan
                (127, 255, 212) # Aquamarine
            ],
            "forest": [
                (0, 100, 0),    # Dark Green
                (0, 128, 0),    # Green
                (50, 205, 50),  # Lime Green
                (144, 238, 144), # Light Green
                (255, 255, 0)   # Yellow
            ],
            "sunset": [
                (25, 25, 112),  # Midnight Blue
                (138, 43, 226), # Blue Violet
                (255, 0, 255),  # Magenta
                (255, 69, 0),   # Orange Red
                (255, 140, 0)   # Dark Orange
            ],
            "greyscale": [
                (0, 0, 0),      # Black
                (64, 64, 64),   # Dark Grey
                (128, 128, 128), # Medium Grey
                (192, 192, 192), # Light Grey
                (255, 255, 255)  # White
            ]
        }
        
        # Presets
        self.presets = {}
        
        # Load saved settings
        self.load_settings()
        
        # Initialize change tracking
        import time
        self._last_modified = time.time()
        self._update_counter = 0
    
    def xy_to_index(self, x, y):
        """Convert x,y coordinates to pixel index"""
        if self.serpentine_wiring:
            # Serpentine (snake) wiring pattern
            if y % 2 == 0:
                # Even rows: left to right
                return y * self.matrix_width + x
            else:
                # Odd rows: right to left
                return y * self.matrix_width + (self.matrix_width - 1 - x)
        else:
            # Progressive wiring pattern
            return y * self.matrix_width + x
    
    def index_to_xy(self, index):
        """Convert pixel index to x,y coordinates"""
        y = index // self.matrix_width
        x = index % self.matrix_width
        
        if self.serpentine_wiring and y % 2 == 1:
            # Odd rows are reversed in serpentine pattern
            x = self.matrix_width - 1 - x
            
        return x, y
    
    def correct_color(self, r, g, b):
        """Apply color order correction for LED strips"""
        if self.color_order == "GRB":
            # Swap red and green for GRB strips
            return (g, r, b)
        elif self.color_order == "BGR":
            # Swap red and blue for BGR strips
            return (b, g, r)
        elif self.color_order == "BRG":
            return (b, r, g)
        elif self.color_order == "RBG":
            return (r, b, g)
        elif self.color_order == "GBR":
            return (g, b, r)
        else:
            # Default RGB order
            return (r, g, b)
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color values"""
        h = h / 360.0  # Convert to 0-1 range
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        # Clamp values to ensure they're in 0-255 range
        r = max(0, min(255, int(r * 255)))
        g = max(0, min(255, int(g * 255)))
        b = max(0, min(255, int(b * 255)))
        return r, g, b
    
    def rgb_to_hsv(self, r, g, b):
        """Convert RGB to HSV color values"""
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return h * 360.0, s, v
    
    def get_palette_color(self, position):
        """Get color from current palette at position (0.0-1.0)"""
        palette = self.palettes.get(self.current_palette, self.palettes["rainbow"])
        
        if len(palette) == 0:
            return (255, 255, 255)
        
        if len(palette) == 1:
            return palette[0]
        
        # Calculate position in palette
        scaled_pos = position * (len(palette) - 1)
        index = int(scaled_pos)
        frac = scaled_pos - index
        
        # Clamp to valid range
        index = max(0, min(index, len(palette) - 2))
        
        # Interpolate between colors
        color1 = palette[index]
        color2 = palette[index + 1]
        
        r = int(color1[0] + (color2[0] - color1[0]) * frac)
        g = int(color1[1] + (color2[1] - color1[1]) * frac)
        b = int(color1[2] + (color2[2] - color1[2]) * frac)
        
        return (r, g, b)
    
    def load_settings(self):
        """Load settings from settings.json"""
        settings_file = Path("settings.json")
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    data = json.load(f)
                    
                    # Load matrix settings
                    self.matrix_width = data.get('matrix_width', self.matrix_width)
                    self.matrix_height = data.get('matrix_height', self.matrix_height)
                    self.serpentine_wiring = data.get('serpentine_wiring', self.serpentine_wiring)
                    
                    # Load animation settings
                    self.brightness = data.get('brightness', self.brightness)
                    self.gamma = data.get('gamma', self.gamma)
                    self.fps = data.get('fps', self.fps)
                    self.current_program = data.get('current_program', self.current_program)
                    
                    # Load color settings
                    self.hue_offset = data.get('hue_offset', self.hue_offset)
                    self.saturation = data.get('saturation', self.saturation)
                    self.current_palette = data.get('current_palette', self.current_palette)
                    
                    # Load animation parameters
                    self.speed = data.get('speed', self.speed)
                    self.scale = data.get('scale', self.scale)
                    self.blend_mode = data.get('blend_mode', self.blend_mode)
                    
                    # Load web server settings
                    self.web_port = data.get('web_port', self.web_port)
                    
                    # Load color order settings
                    self.color_order = data.get('color_order', self.color_order)
                    
                    # Load custom palettes
                    if 'palettes' in data:
                        if isinstance(data['palettes'], dict):
                            self.palettes.update(data['palettes'])
                        else:
                            print(f"⚠️  Invalid palettes data type: {type(data['palettes'])}")
                    
                    # Load presets
                    presets_data = data.get('presets', {})
                    if isinstance(presets_data, dict):
                        self.presets = presets_data
                    else:
                        print(f"⚠️  Invalid presets data type: {type(presets_data)}")
                        self.presets = {}
                    
                print("✅ Settings loaded from settings.json")
            except Exception as e:
                print(f"⚠️  Failed to load settings: {e}")
    
    def save_settings(self):
        """Save settings to settings.json"""
        try:
            data = {
                'matrix_width': self.matrix_width,
                'matrix_height': self.matrix_height,
                'serpentine_wiring': self.serpentine_wiring,
                'brightness': self.brightness,
                'gamma': self.gamma,
                'fps': self.fps,
                'current_program': self.current_program,
                'hue_offset': self.hue_offset,
                'saturation': self.saturation,
                'current_palette': self.current_palette,
                'speed': self.speed,
                'scale': self.scale,
                'blend_mode': self.blend_mode,
                'web_port': self.web_port,
                'color_order': self.color_order,
                'palettes': self.palettes,
                'presets': self.presets
            }
            
            with open("settings.json", 'w') as f:
                json.dump(data, f, indent=2)
                
            print("✅ Settings saved to settings.json")
        except Exception as e:
            print(f"❌ Failed to save settings: {e}")
    
    def mark_updated(self):
        """Mark configuration as updated for change detection"""
        import time
        self._last_modified = time.time()
        self._update_counter += 1
    
    def has_updates(self, last_check_time=0, last_counter=0):
        """Check if configuration has been updated since last check"""
        return (self._last_modified > last_check_time or 
                self._update_counter > last_counter)
    
    def create_preset(self, name):
        """Create a preset from current settings"""
        self.presets[name] = {
            'brightness': self.brightness,
            'gamma': self.gamma,
            'fps': self.fps,
            'current_program': self.current_program,
            'hue_offset': self.hue_offset,
            'saturation': self.saturation,
            'current_palette': self.current_palette,
            'speed': self.speed,
            'scale': self.scale,
            'blend_mode': self.blend_mode
        }
        self.save_settings()
    
    def load_preset(self, name):
        """Load a preset"""
        if name in self.presets:
            preset = self.presets[name]
            
            self.brightness = preset.get('brightness', self.brightness)
            self.gamma = preset.get('gamma', self.gamma)
            self.fps = preset.get('fps', self.fps)
            self.current_program = preset.get('current_program', self.current_program)
            self.hue_offset = preset.get('hue_offset', self.hue_offset)
            self.saturation = preset.get('saturation', self.saturation)
            self.current_palette = preset.get('current_palette', self.current_palette)
            self.speed = preset.get('speed', self.speed)
            self.scale = preset.get('scale', self.scale)
            self.blend_mode = preset.get('blend_mode', self.blend_mode)
            
            return True
        return False
    
    def get_config_dict(self):
        """Get configuration as dictionary for API"""
        # Ensure palettes and presets are dictionaries
        if not isinstance(self.palettes, dict):
            print(f"⚠️  palettes is not a dict: {type(self.palettes)}")
            self.palettes = {}
        if not isinstance(self.presets, dict):
            print(f"⚠️  presets is not a dict: {type(self.presets)}")
            self.presets = {}
            
        return {
            'matrix_width': self.matrix_width,
            'matrix_height': self.matrix_height,
            'serpentine_wiring': self.serpentine_wiring,
            'brightness': self.brightness,
            'gamma': self.gamma,
            'fps': self.fps,
            'current_program': self.current_program,
            'hue_offset': self.hue_offset,
            'saturation': self.saturation,
            'current_palette': self.current_palette,
            'speed': self.speed,
            'scale': self.scale,
            'blend_mode': self.blend_mode,
            'available_palettes': list(self.palettes.keys()),
            'presets': list(self.presets.keys())
        }

def save_stats(stats):
    """Save runtime statistics to /tmp/cosmic_stats.json"""
    try:
        stats_file = Path("/tmp/cosmic_stats.json")
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        print(f"⚠️  Failed to save stats: {e}")

def load_stats():
    """Load runtime statistics from /tmp/cosmic_stats.json"""
    try:
        stats_file = Path("/tmp/cosmic_stats.json")
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️  Failed to load stats: {e}")
    
    return {}