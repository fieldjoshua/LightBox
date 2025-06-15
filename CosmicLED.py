#!/usr/bin/env python3
"""
CosmicLED - Main animation engine for WS2811/NeoPixel LED matrix
Supports hot-swappable animation programs and web GUI control
"""

import time
import json
import threading
import importlib.util
import sys
import os
from pathlib import Path
import traceback
import signal

try:
    import board
    import neopixel
    GPIO_AVAILABLE = True
except ImportError:
    print("⚠️  GPIO libraries not available - running in simulation mode")
    GPIO_AVAILABLE = False

from config import Config, save_stats
from webgui.app import create_app

class LEDMatrix:
    def __init__(self, config):
        self.config = config
        self.pixels = None
        self.running = False
        self.current_program = None
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        
        self.init_hardware()
        self.load_program()
        
    def init_hardware(self):
        """Initialize LED matrix hardware"""
        if GPIO_AVAILABLE:
            try:
                self.pixels = neopixel.NeoPixel(
                    board.D18,  # GPIO 18
                    self.config.matrix_width * self.config.matrix_height,
                    brightness=self.config.brightness,
                    auto_write=False,
                    pixel_order=neopixel.GRB
                )
                print(f"✅ LED matrix initialized: {self.config.matrix_width}x{self.config.matrix_height}")
            except Exception as e:
                print(f"❌ Failed to initialize LED matrix: {e}")
                self.pixels = None
        else:
            # Simulation mode - create dummy pixel array
            self.pixels = [(0, 0, 0)] * (self.config.matrix_width * self.config.matrix_height)
            print(f"🔧 Running in simulation mode: {self.config.matrix_width}x{self.config.matrix_height}")
    
    def load_program(self, program_name=None):
        """Load animation program"""
        if program_name is None:
            program_name = self.config.current_program
            
        program_path = Path("scripts") / f"{program_name}.py"
        
        try:
            if program_path.exists():
                # Load external program
                spec = importlib.util.spec_from_file_location(program_name, program_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.current_program = module
                print(f"✅ Loaded program: {program_name}")
            else:
                # Fall back to built-in cosmic animation
                self.current_program = self.get_builtin_cosmic()
                print(f"🌟 Using built-in cosmic animation")
                
            self.config.current_program = program_name
            
        except Exception as e:
            print(f"❌ Failed to load program {program_name}: {e}")
            self.current_program = self.get_builtin_cosmic()
            
    def get_builtin_cosmic(self):
        """Built-in cosmic flowing animation"""
        class CosmicProgram:
            @staticmethod
            def animate(pixels, config, frame):
                """Cosmic flowing colors animation"""
                import math
                
                for y in range(config.matrix_height):
                    for x in range(config.matrix_width):
                        # Create flowing wave pattern
                        wave1 = math.sin((x + frame * 0.1) * 0.3) * 0.5 + 0.5
                        wave2 = math.sin((y + frame * 0.08) * 0.25) * 0.5 + 0.5
                        wave3 = math.sin((x + y + frame * 0.12) * 0.2) * 0.5 + 0.5
                        
                        # Combine waves for color
                        hue_offset = (wave1 + wave2 + wave3) / 3
                        hue = (config.hue_offset + hue_offset * 360) % 360
                        
                        # Convert HSV to RGB
                        r, g, b = config.hsv_to_rgb(hue, config.saturation, config.brightness_scale)
                        
                        # Apply gamma correction
                        r = int(pow(r / 255.0, config.gamma) * 255)
                        g = int(pow(g / 255.0, config.gamma) * 255)
                        b = int(pow(b / 255.0, config.gamma) * 255)
                        
                        # Set pixel
                        pixel_index = config.xy_to_index(x, y)
                        if GPIO_AVAILABLE and hasattr(pixels, '__setitem__'):
                            pixels[pixel_index] = (r, g, b)
                        else:
                            pixels[pixel_index] = (r, g, b)
                            
        return CosmicProgram()
    
    def start(self):
        """Start animation loop"""
        self.running = True
        print("🎨 Starting animation loop...")
        
        try:
            while self.running:
                start_time = time.time()
                
                # Run animation program
                if self.current_program and hasattr(self.current_program, 'animate'):
                    try:
                        self.current_program.animate(self.pixels, self.config, self.frame_count)
                        
                        # Show pixels (if real hardware)
                        if GPIO_AVAILABLE and self.pixels and hasattr(self.pixels, 'show'):
                            self.pixels.show()
                            
                    except Exception as e:
                        print(f"❌ Animation error: {e}")
                        # Fall back to built-in animation
                        self.current_program = self.get_builtin_cosmic()
                
                # Update frame counter and FPS
                self.frame_count += 1
                self.fps_counter += 1
                
                # Calculate FPS every second
                current_time = time.time()
                if current_time - self.last_fps_time >= 1.0:
                    self.current_fps = self.fps_counter
                    self.fps_counter = 0
                    self.last_fps_time = current_time
                    
                    # Save runtime stats
                    self.save_runtime_stats()
                
                # Control frame rate
                elapsed = time.time() - start_time
                sleep_time = max(0, (1.0 / self.config.fps) - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            print("\n⏹️  Animation stopped by user")
        except Exception as e:
            print(f"❌ Animation loop error: {e}")
            traceback.print_exc()
        finally:
            self.stop()
    
    def stop(self):
        """Stop animation and cleanup"""
        self.running = False
        if GPIO_AVAILABLE and self.pixels:
            # Clear all pixels
            self.pixels.fill((0, 0, 0))
            self.pixels.show()
        print("✅ Animation stopped")
    
    def save_runtime_stats(self):
        """Save runtime statistics"""
        stats = {
            'fps': self.current_fps,
            'frame_count': self.frame_count,
            'program': self.config.current_program,
            'brightness': self.config.brightness,
            'timestamp': time.time()
        }
        save_stats(stats)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n📶 Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point"""
    print("🌟 CosmicLED Starting...")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize configuration
    config = Config()
    
    # Create LED matrix
    matrix = LEDMatrix(config)
    
    # Start web GUI in separate thread
    app = create_app(matrix, config)
    web_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, threaded=True),
        daemon=True
    )
    web_thread.start()
    print("🌐 Web interface started at http://localhost:5000")
    
    # Start animation loop (blocking)
    try:
        matrix.start()
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down...")
    finally:
        matrix.stop()

if __name__ == "__main__":
    main()