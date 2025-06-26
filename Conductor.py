#!/usr/bin/env python3
"""
Conductor - Modern main controller for the LED matrix system
Initializes config, hardware, animation, and (optionally) web interface
"""

import time
import threading
import signal
import sys
import os
import importlib.util
import traceback
from pathlib import Path
from logging_config import setup_logging, get_logger, log_startup, log_shutdown, log_performance

from config import Config, save_stats
try:
    from webgui.app import create_app
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

# Improved GPIO detection with better error handling
GPIO_AVAILABLE = False
WS281X_AVAILABLE = False

# Try to detect if we're on a Raspberry Pi
def is_raspberry_pi():
    """Check if we're running on a Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except:
        return False

# Only try GPIO imports if we're on a Raspberry Pi - use Blinka NeoPixel
if is_raspberry_pi():
    try:
        import board
        import neopixel
        GPIO_AVAILABLE = True
        print("✅ Blinka NeoPixel library loaded successfully")
    except ImportError as e:
        print(f"⚠️  Blinka NeoPixel library not available: {e}")
        GPIO_AVAILABLE = False
    except Exception as e:
        print(f"⚠️  Blinka NeoPixel initialization failed: {e}")
        GPIO_AVAILABLE = False
else:
    print("🔧 Not running on Raspberry Pi - using simulation mode")


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
        
        # Configuration change tracking
        self.last_config_check = time.time()
        self.last_config_counter = 0
        
        # Setup component-specific loggers
        self.logger = get_logger('animation')
        self.hardware_logger = get_logger('hardware')
        self.error_logger = get_logger('errors')
        
        self.init_hardware()
        self.load_program()
        
    def init_hardware(self):
        """Initialize LED matrix hardware using Blinka NeoPixel"""
        if GPIO_AVAILABLE:
            try:
                led_count = self.config.matrix_width * self.config.matrix_height

                # GPIO12 for LED data as per hardware setup (board.D12)
                self.pixels = neopixel.NeoPixel(
                    board.D12, 
                    led_count, 
                    brightness=self.config.brightness,
                    auto_write=False
                )
                
                self.hardware_logger.info(
                    f"LED matrix initialized (NeoPixel): {self.config.matrix_width}x{self.config.matrix_height}"
                )
                print(f"✅ LED matrix initialized (NeoPixel): {self.config.matrix_width}x{self.config.matrix_height}")
                return
            except Exception as e:
                self.error_logger.error(f"NeoPixel initialization failed: {e}")
                print(f"❌ NeoPixel init failed: {e}")
                self.pixels = None

        # If hardware init failed, enter simulation mode
        if self.pixels is None:
            self.pixels = [(0, 0, 0)] * (
                self.config.matrix_width * self.config.matrix_height
            )
            print(
                f"🔧 Running in simulation mode: {self.config.matrix_width}x{self.config.matrix_height}"
            )
    
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
                self.config.current_program = program_name
            else:
                # Try to find any available program
                scripts_dir = Path("scripts")
                if scripts_dir.exists():
                    available_programs = [f.stem for f in scripts_dir.glob("*.py") if f.name != "__init__.py"]
                    if available_programs:
                        fallback_program = available_programs[0]
                        print(f"⚠️  Program '{program_name}' not found, using '{fallback_program}' instead")
                        return self.load_program(fallback_program)
                
                print(f"❌ No animation programs found in scripts/ directory")
                self.current_program = None
                
        except Exception as e:
            print(f"❌ Failed to load program {program_name}: {e}")
            # Try to find any working program as fallback
            scripts_dir = Path("scripts")
            if scripts_dir.exists():
                available_programs = [f.stem for f in scripts_dir.glob("*.py") if f.name != "__init__.py"]
                for fallback in available_programs:
                    if fallback != program_name:  # Don't retry the same program
                        try:
                            print(f"🔄 Trying fallback program: {fallback}")
                            return self.load_program(fallback)
                        except:
                            continue
            
            print(f"❌ No working animation programs found")
            self.current_program = None
            
    
    def check_config_updates(self):
        """Check for configuration updates and apply them"""
        if self.config.has_updates(self.last_config_check, self.last_config_counter):
            print("🔄 Configuration updated - applying changes")
            
            # Update hardware brightness if available
            if GPIO_AVAILABLE and self.pixels and hasattr(self.pixels, 'brightness'):
                try:
                    self.pixels.brightness = self.config.brightness
                    print(f"✅ Updated hardware brightness to {self.config.brightness}")
                except Exception as e:
                    print(f"⚠️  Failed to update hardware brightness: {e}")
            
            # Update tracking
            self.last_config_check = time.time()
            self.last_config_counter = self.config._update_counter
            
            return True
        return False
    
    def clamp_pixels(self):
        """Clamp all pixel values to 0-255 and ensure valid RGB tuples"""
        if self.pixels is None:
            return
        try:
            # For NeoPixel hardware, values are automatically clamped
            # Only validate for simulation mode (list-based pixels)
            if isinstance(self.pixels, list):
                invalid_count = 0
                for i in range(len(self.pixels)):
                    pix = self.pixels[i]
                    if (isinstance(pix, (tuple, list)) and len(pix) == 3 and
                        all(isinstance(v, (int, float)) for v in pix)):
                        r = int(max(0, min(255, pix[0])))
                        g = int(max(0, min(255, pix[1])))
                        b = int(max(0, min(255, pix[2])))
                        
                        # Check for out-of-range values
                        if pix[0] < 0 or pix[0] > 255 or pix[1] < 0 or pix[1] > 255 or pix[2] < 0 or pix[2] > 255:
                            invalid_count += 1
                            if invalid_count <= 3:  # Only show first few errors to avoid spam
                                print(f"⚠️  Clamped out-of-range pixel at {i}: {pix} -> ({r},{g},{b})")
                        
                        self.pixels[i] = (r, g, b)
                    else:
                        print(f"⚠️  Invalid pixel value at index {i}: {pix}, resetting to (0,0,0)")
                        self.pixels[i] = (0, 0, 0)
                        
                if invalid_count > 3:
                    print(f"⚠️  Clamped {invalid_count} total out-of-range pixels this frame")
                
        except Exception as e:
            print(f"⚠️  Error in clamp_pixels: {e}")
    
    @staticmethod
    def safe_color(r, g, b):
        """Utility function for animations to ensure safe color values"""
        return (
            int(max(0, min(255, r))),
            int(max(0, min(255, g))),
            int(max(0, min(255, b)))
        )
    
    def start(self):
        """Start animation loop"""
        self.running = True
        print("🎨 Starting animation loop...")
        
        try:
            while self.running:
                start_time = time.time()
                
                # Check for configuration updates
                self.check_config_updates()
                
                # Run animation program
                if self.current_program and hasattr(self.current_program, 'animate'):
                    try:
                        self.current_program.animate(self.pixels, self.config, self.frame_count)
                        
                        # Show pixels (if real hardware)
                        if GPIO_AVAILABLE and self.pixels and hasattr(self.pixels, 'show'):
                            self.clamp_pixels()
                            self.pixels.show()
                            # Debug: Print show() call success
                            if self.frame_count % 30 == 0:  # Every 30 frames
                                print(f"🌟 Frame {self.frame_count}: pixels.show() called successfully")
                        else:
                            if self.frame_count % 30 == 0:
                                print(f"⚠️  Frame {self.frame_count}: pixels.show() NOT called - GPIO_AVAILABLE: {GPIO_AVAILABLE}, has_show: {hasattr(self.pixels, 'show') if self.pixels else False}")
                            
                    except Exception as e:
                        print(f"❌ Animation error in {getattr(self.current_program, '__name__', 'unknown')}: {e}")
                        print(f"   Error type: {type(e).__name__}")
                        if "byte must be in range" in str(e):
                            print("   🔍 Color range error detected - this animation needs color validation fixes")
                        
                        # Try to load a different working program
                        scripts_dir = Path("scripts")
                        if scripts_dir.exists():
                            available_programs = [f.stem for f in scripts_dir.glob("*.py") if f.name != "__init__.py"]
                            current_name = getattr(self.current_program, '__name__', self.config.current_program)
                            for fallback in available_programs:
                                if fallback != current_name:
                                    try:
                                        print(f"   🔄 Trying fallback program: {fallback}")
                                        self.load_program(fallback)
                                        break
                                    except:
                                        continue
                            else:
                                print("   ❌ No working fallback programs found")
                                self.current_program = None
                        else:
                            print("   ❌ No scripts directory found")
                            self.current_program = None
                else:
                    # No program loaded - fill with black and wait
                    if self.frame_count % 60 == 0:  # Every 4 seconds at 15fps
                        print("⚠️  No animation program loaded - LEDs off")
                    if self.pixels:
                        if hasattr(self.pixels, 'fill'):
                            self.pixels.fill((0, 0, 0))
                        else:
                            for i in range(len(self.pixels)):
                                self.pixels[i] = (0, 0, 0)
                    if GPIO_AVAILABLE and self.pixels and hasattr(self.pixels, 'show'):
                        self.pixels.show()
                
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
        
        # Log performance metrics
        try:
            import psutil
            memory_mb = psutil.virtual_memory().used / (1024 * 1024)
            cpu_percent = psutil.cpu_percent(interval=None)
            log_performance(self.current_fps, memory_mb, cpu_percent, self.frame_count)
        except ImportError:
            # psutil not available, log basic metrics
            log_performance(self.current_fps, 0, 0, self.frame_count)


def signal_handler(signum, frame):
    print(f"\n📶 Received signal {signum}, shutting down...")
    sys.exit(0)


def kill_port(port):
    """Kill any process using the specified port (Safe version for service)"""
    print(f"🧹 Checking port {port}...")
    
    try:
        import subprocess
        import os
        
        # Only try to kill ports if not running as root service (avoid conflicts)
        if os.geteuid() == 0:
            print(f"⚠️  Running as root - skipping aggressive port clearing")
            return
        
        # Method 1: Using lsof with regular privileges
        result = subprocess.run([
            'lsof', '-ti', f':{port}'
        ], capture_output=True, text=True)
        
        pids = [pid.strip() for pid in result.stdout.strip().split('\n') if pid.strip()]
        
        if pids:
            for pid in pids:
                print(f"🔪 Found process on port {port}: PID {pid}")
                try:
                    # Only try gentle kill, no sudo
                    subprocess.run(['kill', '-TERM', pid], check=True)
                    print(f"✅ Sent TERM signal to PID {pid}")
                except subprocess.CalledProcessError:
                    print(f"⚠️  Could not signal PID {pid} (process may not be ours)")
        else:
            print(f"✅ Port {port} is already free")
            
    except FileNotFoundError:
        print("⚠️  lsof not available - skipping port check")
    except Exception as e:
        print(f"⚠️  Port check failed: {e}")
    
    # Add a small delay
    import time
    time.sleep(0.2)
    print(f"🚀 Port {port} check complete")


def main(with_web=True):
    # Setup logging first
    setup_logging()
    
    # Initialize configuration
    config = Config()
    
    # Log startup with configuration summary
    config_summary = {
        'matrix_size': f"{config.matrix_width}x{config.matrix_height}",
        'web_port': config.web_port,
        'fps': config.fps,
        'brightness': config.brightness,
        'current_program': config.current_program
    }
    log_startup("1.0", config_summary)
    
    print("🎼 Conductor Starting...")

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Kill any process using the web port
    if with_web:
        kill_port(config.web_port)

    # Create LED matrix
    matrix = LEDMatrix(config)

    # Start web GUI in a separate process if requested
    web_process = None
    if with_web and WEB_AVAILABLE:
        try:
            import multiprocessing
            import subprocess
            
            # Start web interface as separate process to avoid threading issues
            def start_web_server():
                try:
                    app = create_app(matrix, config)
                    app.run(
                        host='0.0.0.0',
                        port=config.web_port,
                        debug=False,
                        threaded=True,
                        use_reloader=False
                    )
                except Exception as e:
                    print(f"❌ Web server error: {e}")
            
            # Try threading first (simpler)
            web_thread = threading.Thread(target=start_web_server, daemon=True)
            web_thread.start()
            
            # Give web server time to start
            time.sleep(2)
            
            print(f"🌐 Web interface started at http://localhost:{config.web_port}")
            print(f"🌐 External access: http://192.168.0.222:{config.web_port}")
            
        except Exception as e:
            print(f"⚠️  Failed to start web interface: {e}")
            with_web = False
    elif with_web:
        print("⚠️  Web interface not available (Flask not installed)")

    # Start animation loop (blocking)
    try:
        matrix.start()
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down...")
        log_shutdown()
    finally:
        matrix.stop()
        if web_process:
            try:
                web_process.terminate()
                web_process.join(timeout=5)
            except:
                pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Conductor - LED Matrix Main Controller"
    )
    parser.add_argument(
        '--no-web',
        action='store_true',
        help='Run without web interface'
    )
    args = parser.parse_args()
    main(with_web=not args.no_web) 