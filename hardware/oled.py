"""
OLED Display integration for CosmicLED
Shows status information, current program, and system stats
"""

import time
import threading
from pathlib import Path

try:
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    OLED_AVAILABLE = True
except ImportError:
    print("⚠️  OLED libraries not available - display disabled")
    OLED_AVAILABLE = False

class OLEDDisplay:
    """Handles OLED status display for LED matrix"""
    
    def __init__(self, config, matrix=None):
        self.config = config
        self.matrix = matrix
        self.running = False
        self.display_thread = None
        self.display = None
        
        # Display settings
        self.width = 128
        self.height = 64
        self.update_interval = 1.0  # Update every second
        
        # Screen rotation and layout
        self.current_screen = 0
        self.screen_count = 4
        self.auto_rotate = True
        self.screen_duration = 3.0  # 3 seconds per screen
        self.last_screen_change = time.time()
        
        if OLED_AVAILABLE:
            self.setup_display()
    
    def setup_display(self):
        """Initialize OLED display"""
        try:
            # Create I2C interface
            i2c = board.I2C()
            
            # Create SSD1306 display object
            self.display = adafruit_ssd1306.SSD1306_I2C(
                self.width, self.height, i2c, addr=0x3C
            )
            
            # Clear display
            self.display.fill(0)
            self.display.show()
            
            print("✅ OLED display initialized")
            
        except Exception as e:
            print(f"❌ Failed to setup OLED display: {e}")
            self.display = None
            raise
    
    def start(self):
        """Start display update thread"""
        if not OLED_AVAILABLE or not self.display:
            print("⚠️  OLED display not available")
            return
            
        self.running = True
        self.display_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.display_thread.start()
        print("📺 OLED display started")
    
    def stop(self):
        """Stop display updates and clear screen"""
        self.running = False
        
        if self.display_thread:
            self.display_thread.join(timeout=1.0)
            
        if self.display:
            self.display.fill(0)
            self.display.show()
            print("✅ OLED display stopped")
    
    def _update_loop(self):
        """Main display update loop"""
        while self.running:
            try:
                current_time = time.time()
                
                # Auto-rotate screens
                if self.auto_rotate and current_time - self.last_screen_change > self.screen_duration:
                    self.current_screen = (self.current_screen + 1) % self.screen_count
                    self.last_screen_change = current_time
                
                # Update display
                self._update_display()
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"❌ OLED update error: {e}")
                time.sleep(1.0)
    
    def _update_display(self):
        """Update display content based on current screen"""
        if not self.display:
            return
            
        # Create image for drawing
        image = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        # Load fonts (fallback to default if not found)
        try:
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
            font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10)
        except:
            # Use default font if custom fonts not available
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Render different screens
        if self.current_screen == 0:
            self._draw_status_screen(draw, font_large, font_medium, font_small)
        elif self.current_screen == 1:
            self._draw_program_screen(draw, font_large, font_medium, font_small)
        elif self.current_screen == 2:
            self._draw_settings_screen(draw, font_large, font_medium, font_small)
        elif self.current_screen == 3:
            self._draw_stats_screen(draw, font_large, font_medium, font_small)
        
        # Convert image to display format and show
        self.display.image(image)
        self.display.show()
    
    def _draw_status_screen(self, draw, font_large, font_medium, font_small):
        """Draw main status screen"""
        # Title
        draw.text((0, 0), "CosmicLED", font=font_large, fill=255)
        
        # Status indicator
        status = "Running" if (self.matrix and self.matrix.running) else "Stopped"
        draw.text((0, 20), f"Status: {status}", font=font_medium, fill=255)
        
        # FPS and frame count
        from config import load_stats
        stats = load_stats()
        fps = stats.get('fps', 0)
        frame_count = stats.get('frame_count', 0)
        
        draw.text((0, 35), f"FPS: {fps}", font=font_medium, fill=255)
        draw.text((0, 50), f"Frames: {frame_count}", font=font_small, fill=255)
        
        # Screen indicator dots
        self._draw_screen_indicators(draw, 100, 0)
    
    def _draw_program_screen(self, draw, font_large, font_medium, font_small):
        """Draw program information screen"""
        # Title
        draw.text((0, 0), "Program", font=font_large, fill=255)
        
        # Current program
        program = self.config.current_program or "cosmic"
        # Truncate long program names
        if len(program) > 12:
            program = program[:9] + "..."
        draw.text((0, 20), f"Current:", font=font_medium, fill=255)
        draw.text((0, 35), program, font=font_medium, fill=255)
        
        # Matrix size
        matrix_size = f"{self.config.matrix_width}x{self.config.matrix_height}"
        draw.text((0, 50), f"Matrix: {matrix_size}", font=font_small, fill=255)
        
        # Screen indicator dots
        self._draw_screen_indicators(draw, 100, 0)
    
    def _draw_settings_screen(self, draw, font_large, font_medium, font_small):
        """Draw settings screen"""
        # Title
        draw.text((0, 0), "Settings", font=font_large, fill=255)
        
        # Brightness
        brightness_pct = int(self.config.brightness * 100)
        draw.text((0, 20), f"Brightness: {brightness_pct}%", font=font_small, fill=255)
        
        # Speed
        speed = self.config.speed
        draw.text((0, 32), f"Speed: {speed:.1f}x", font=font_small, fill=255)
        
        # Palette
        palette = self.config.current_palette or "rainbow"
        if len(palette) > 10:
            palette = palette[:7] + "..."
        draw.text((0, 44), f"Palette: {palette}", font=font_small, fill=255)
        
        # FPS
        draw.text((0, 56), f"FPS: {self.config.fps}", font=font_small, fill=255)
        
        # Screen indicator dots
        self._draw_screen_indicators(draw, 100, 0)
    
    def _draw_stats_screen(self, draw, font_large, font_medium, font_small):
        """Draw system statistics screen"""
        # Title
        draw.text((0, 0), "System", font=font_large, fill=255)
        
        # Get system stats
        from config import load_stats
        stats = load_stats()
        
        # Uptime
        uptime = stats.get('timestamp', time.time())
        uptime_seconds = time.time() - uptime
        uptime_str = self._format_uptime(uptime_seconds)
        draw.text((0, 20), f"Uptime: {uptime_str}", font=font_small, fill=255)
        
        # Memory usage (if available)
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_pct = int(memory.percent)
            draw.text((0, 32), f"Memory: {memory_pct}%", font=font_small, fill=255)
        except ImportError:
            draw.text((0, 32), "Memory: N/A", font=font_small, fill=255)
        
        # Temperature (if available)
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_c = int(f.read()) / 1000.0
                draw.text((0, 44), f"Temp: {temp_c:.1f}°C", font=font_small, fill=255)
        except:
            draw.text((0, 44), "Temp: N/A", font=font_small, fill=255)
        
        # Total pixels
        total_pixels = self.config.matrix_width * self.config.matrix_height
        draw.text((0, 56), f"Pixels: {total_pixels}", font=font_small, fill=255)
        
        # Screen indicator dots
        self._draw_screen_indicators(draw, 100, 0)
    
    def _draw_screen_indicators(self, draw, x, y):
        """Draw screen indicator dots"""
        dot_size = 3
        dot_spacing = 6
        
        for i in range(self.screen_count):
            dot_x = x + i * dot_spacing
            dot_y = y
            
            if i == self.current_screen:
                # Fill current screen dot
                draw.ellipse([dot_x, dot_y, dot_x + dot_size, dot_y + dot_size], fill=255)
            else:
                # Outline other dots
                draw.ellipse([dot_x, dot_y, dot_x + dot_size, dot_y + dot_size], outline=255)
    
    def _format_uptime(self, seconds):
        """Format uptime in human readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m"
        elif seconds < 86400:
            return f"{int(seconds/3600)}h"
        else:
            return f"{int(seconds/86400)}d"
    
    def set_screen(self, screen_number):
        """Manually set display screen"""
        if 0 <= screen_number < self.screen_count:
            self.current_screen = screen_number
            self.last_screen_change = time.time()
    
    def next_screen(self):
        """Manually advance to next screen"""
        self.current_screen = (self.current_screen + 1) % self.screen_count
        self.last_screen_change = time.time()
    
    def set_auto_rotate(self, enabled):
        """Enable or disable automatic screen rotation"""
        self.auto_rotate = enabled
    
    def show_message(self, message, duration=3.0):
        """Show a temporary message on display"""
        if not self.display:
            return
            
        # Save current state
        old_auto_rotate = self.auto_rotate
        self.auto_rotate = False
        
        try:
            # Create message screen
            image = Image.new('1', (self.width, self.height))
            draw = ImageDraw.Draw(image)
            
            # Load font
            try:
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
            except:
                font = ImageFont.load_default()
            
            # Word wrap the message
            lines = self._wrap_text(message, font, self.width - 10)
            
            # Draw message
            y = 10
            for line in lines:
                draw.text((5, y), line, font=font, fill=255)
                y += 15
                if y > self.height - 15:
                    break
            
            # Show message
            self.display.image(image)
            self.display.show()
            
            # Wait for duration
            time.sleep(duration)
            
        finally:
            # Restore auto-rotate
            self.auto_rotate = old_auto_rotate
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = ''
        
        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            
            # Use textsize for older PIL versions, textbbox for newer
            try:
                width = font.getbbox(test_line)[2]
            except AttributeError:
                width, _ = font.getsize(test_line)
            
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines

# Example usage and testing
if __name__ == "__main__":
    # Simple test program
    print("📺 OLED Display Test")
    print("Press Ctrl+C to exit")
    
    from config import Config
    
    config = Config()
    display = OLEDDisplay(config)
    
    try:
        display.start()
        
        # Test message display
        time.sleep(2)
        display.show_message("Hello CosmicLED!", 2)
        
        # Let it run and cycle through screens
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping OLED display...")
        display.stop()
        print("✅ Test completed")