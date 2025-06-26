"""
GPIO Button integration for LightBox LED Matrix
Handles physical button controls for brightness, mode switching, and speed
"""

import time
import threading
from pathlib import Path

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    print("⚠️  RPi.GPIO not available - button controls disabled")
    GPIO_AVAILABLE = False

class ButtonController:
    """Handles GPIO button inputs for LED matrix control"""
    
    def __init__(self, config, matrix=None):
        self.config = config
        self.matrix = matrix
        self.running = False
        self.button_thread = None
        
        # Button pin assignments (BCM numbering)
        self.buttons = {
            'brightness': 21,   # Brightness up/down
            'mode': 20,         # Switch animation program
            'speed': 16,        # Speed adjustment
            'preset': 12        # Load next preset  
        }
        
        # Button state tracking
        self.button_states = {}
        self.last_press_time = {}
        self.press_count = {}
        
        # Timing constants
        self.debounce_time = 0.05  # 50ms debounce
        self.double_click_time = 0.5  # 500ms for double-click detection
        self.long_press_time = 2.0  # 2s for long press
        
        if GPIO_AVAILABLE:
            self.setup_gpio()
    
    def setup_gpio(self):
        """Initialize GPIO pins for button inputs"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            for button_name, pin in self.buttons.items():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                self.button_states[button_name] = True  # Pull-up means True when not pressed
                self.last_press_time[button_name] = 0
                self.press_count[button_name] = 0
                
            print("✅ GPIO buttons initialized")
            
        except Exception as e:
            print(f"❌ Failed to setup GPIO buttons: {e}")
            raise
    
    def start(self):
        """Start button monitoring thread"""
        if not GPIO_AVAILABLE:
            print("⚠️  Button controller not available")
            return
            
        self.running = True
        self.button_thread = threading.Thread(target=self._monitor_buttons, daemon=True)
        self.button_thread.start()
        print("🎛️  Button monitoring started")
    
    def stop(self):
        """Stop button monitoring and cleanup GPIO"""
        self.running = False
        
        if self.button_thread:
            self.button_thread.join(timeout=1.0)
            
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            print("✅ Button monitoring stopped")
    
    def _monitor_buttons(self):
        """Main button monitoring loop"""
        while self.running:
            try:
                current_time = time.time()
                
                for button_name, pin in self.buttons.items():
                    current_state = GPIO.input(pin)
                    previous_state = self.button_states[button_name]
                    
                    # Detect button press (transition from high to low due to pull-up)
                    if previous_state and not current_state:
                        # Button pressed
                        if current_time - self.last_press_time[button_name] > self.debounce_time:
                            self._handle_button_press(button_name, current_time)
                            self.last_press_time[button_name] = current_time
                    
                    # Detect button release
                    elif not previous_state and current_state:
                        # Button released
                        if current_time - self.last_press_time[button_name] > self.debounce_time:
                            self._handle_button_release(button_name, current_time)
                    
                    self.button_states[button_name] = current_state
                
                time.sleep(0.01)  # 10ms polling interval
                
            except Exception as e:
                print(f"❌ Button monitoring error: {e}")
                time.sleep(0.1)
    
    def _handle_button_press(self, button_name, press_time):
        """Handle button press events"""
        print(f"🔘 Button pressed: {button_name}")
        
        # Increment press count for double-click detection
        if press_time - self.last_press_time[button_name] < self.double_click_time:
            self.press_count[button_name] += 1
        else:
            self.press_count[button_name] = 1
        
        # Handle specific button actions
        if button_name == 'brightness':
            self._handle_brightness_button(press_time)
        elif button_name == 'mode':
            self._handle_mode_button(press_time)
        elif button_name == 'speed':
            self._handle_speed_button(press_time)
        elif button_name == 'preset':
            self._handle_preset_button(press_time)
    
    def _handle_button_release(self, button_name, release_time):
        """Handle button release events"""
        press_duration = release_time - self.last_press_time[button_name]
        
        # Check for long press
        if press_duration > self.long_press_time:
            self._handle_long_press(button_name)
    
    def _handle_brightness_button(self, press_time):
        """Handle brightness button press"""
        press_count = self.press_count['brightness']
        
        if press_count == 1:
            # Single press: increase brightness
            new_brightness = min(1.0, self.config.brightness + 0.1)
            self.config.brightness = new_brightness
            print(f"💡 Brightness: {int(new_brightness * 100)}%")
            
        elif press_count == 2:
            # Double press: decrease brightness
            new_brightness = max(0.1, self.config.brightness - 0.1)
            self.config.brightness = new_brightness
            print(f"💡 Brightness: {int(new_brightness * 100)}%")
        
        self.config.save_settings()
    
    def _handle_mode_button(self, press_time):
        """Handle mode/program button press"""
        if not self.matrix:
            return
            
        # Get available programs
        scripts_dir = Path('scripts')
        programs = ['cosmic']  # Always include built-in cosmic
        
        if scripts_dir.exists():
            for script_file in scripts_dir.glob('*.py'):
                programs.append(script_file.stem)
        
        # Find current program index
        current_index = 0
        try:
            current_index = programs.index(self.config.current_program)
        except ValueError:
            pass
        
        # Switch to next program
        next_index = (current_index + 1) % len(programs)
        next_program = programs[next_index]
        
        print(f"🎨 Switching to program: {next_program}")
        self.matrix.load_program(next_program)
        self.config.save_settings()
    
    def _handle_speed_button(self, press_time):
        """Handle speed button press"""
        press_count = self.press_count['speed']
        
        if press_count == 1:
            # Single press: increase speed
            new_speed = min(5.0, self.config.speed + 0.2)
            self.config.speed = new_speed
            print(f"⚡ Speed: {new_speed:.1f}x")
            
        elif press_count == 2:
            # Double press: decrease speed
            new_speed = max(0.1, self.config.speed - 0.2)
            self.config.speed = new_speed
            print(f"⚡ Speed: {new_speed:.1f}x")
        
        self.config.save_settings()
    
    def _handle_preset_button(self, press_time):
        """Handle preset button press"""
        presets = list(self.config.presets.keys())
        
        if not presets:
            print("📄 No presets available")
            return
        
        # Find current preset or use first one
        current_preset = getattr(self, '_current_preset_index', 0)
        next_preset_index = (current_preset + 1) % len(presets)
        next_preset = presets[next_preset_index]
        
        print(f"📄 Loading preset: {next_preset}")
        if self.config.load_preset(next_preset):
            self._current_preset_index = next_preset_index
        else:
            print(f"❌ Failed to load preset: {next_preset}")
    
    def _handle_long_press(self, button_name):
        """Handle long press events"""
        print(f"🔘 Long press: {button_name}")
        
        if button_name == 'brightness':
            # Long press brightness: reset to 50%
            self.config.brightness = 0.5
            print("💡 Brightness reset to 50%")
            self.config.save_settings()
            
        elif button_name == 'mode':
            # Long press mode: reload current program
            if self.matrix:
                print("🔄 Reloading current program")
                self.matrix.load_program(self.config.current_program)
                
        elif button_name == 'speed':
            # Long press speed: reset to 1.0x
            self.config.speed = 1.0
            print("⚡ Speed reset to 1.0x")
            self.config.save_settings()
            
        elif button_name == 'preset':
            # Long press preset: save current settings as 'Quick' preset
            self.config.create_preset('Quick')
            print("📄 Current settings saved as 'Quick' preset")

# Example usage and testing
if __name__ == "__main__":
    # Simple test program
    print("🎛️  Button Controller Test")
    print("Press Ctrl+C to exit")
    
    from config import Config
    
    config = Config()
    controller = ButtonController(config)
    
    try:
        controller.start()
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping button controller...")
        controller.stop()
        print("✅ Test completed")