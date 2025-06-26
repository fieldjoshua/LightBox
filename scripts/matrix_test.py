# flake8: noqa
"""
Matrix Test Animation for CosmicLED
Hardware verification animation that tests all pixels and wiring patterns
"""

import math

def animate(pixels, config, frame):
    """
    Matrix test animation for hardware verification
    Cycles through different test patterns to verify LED wiring and functionality
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with animation parameters
        frame: Current frame number for animation timing
    """
    
    # Test cycle duration (frames per test)
    test_duration = 60  # 2 seconds at 30fps
    total_tests = 8
    
    # Determine current test
    test_cycle = (frame // test_duration) % total_tests
    test_frame = frame % test_duration
    
    # Clear all pixels first
    total_pixels = config.matrix_width * config.matrix_height
    for i in range(total_pixels):
        try:
            if hasattr(pixels, '__setitem__'):
                pixels[i] = (0, 0, 0)
            else:
                pixels[i] = (0, 0, 0)
        except IndexError:
            pass
    
    if test_cycle == 0:
        # Test 1: All pixels white (brightness test)
        _test_all_white(pixels, config, test_frame)
        
    elif test_cycle == 1:
        # Test 2: RGB color sweep
        _test_rgb_sweep(pixels, config, test_frame)
        
    elif test_cycle == 2:
        # Test 3: Individual pixel scan
        _test_pixel_scan(pixels, config, test_frame)
        
    elif test_cycle == 3:
        # Test 4: Row by row test
        _test_row_scan(pixels, config, test_frame)
        
    elif test_cycle == 4:
        # Test 5: Column by column test
        _test_column_scan(pixels, config, test_frame)
        
    elif test_cycle == 5:
        # Test 6: Wiring pattern test (serpentine vs progressive)
        _test_wiring_pattern(pixels, config, test_frame)
        
    elif test_cycle == 6:
        # Test 7: Corner and edge test
        _test_corners_edges(pixels, config, test_frame)
        
    elif test_cycle == 7:
        # Test 8: Gradient test
        _test_gradient(pixels, config, test_frame)

def _test_all_white(pixels, config, test_frame):
    """Test all pixels with white color at varying brightness"""
    brightness_cycle = math.sin(test_frame * 0.2) * 0.5 + 0.5
    brightness = int(brightness_cycle * 255)
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            pixel_index = config.xy_to_index(x, y)
            try:
                if hasattr(pixels, '__setitem__'):
                    pixels[pixel_index] = (brightness, brightness, brightness)
                else:
                    pixels[pixel_index] = (brightness, brightness, brightness)
            except IndexError:
                pass

def _test_rgb_sweep(pixels, config, test_frame):
    """Sweep through red, green, blue colors"""
    phase = (test_frame / 20.0) % 3  # 3 colors over 60 frames
    brightness = 255
    
    if phase < 1:
        # Red phase
        color = (brightness, 0, 0)
    elif phase < 2:
        # Green phase
        color = (0, brightness, 0)
    else:
        # Blue phase
        color = (0, 0, brightness)
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            pixel_index = config.xy_to_index(x, y)
            try:
                if hasattr(pixels, '__setitem__'):
                    pixels[pixel_index] = (
                        int(max(0, min(255, color[0] * brightness))),
                        int(max(0, min(255, color[1] * brightness))),
                        int(max(0, min(255, color[2] * brightness)))
                    )
                else:
                    pixels[pixel_index] = (
                        int(max(0, min(255, color[0] * brightness))),
                        int(max(0, min(255, color[1] * brightness))),
                        int(max(0, min(255, color[2] * brightness)))
                    )
            except IndexError:
                pass

def _test_pixel_scan(pixels, config, test_frame):
    """Light up one pixel at a time"""
    total_pixels = config.matrix_width * config.matrix_height
    if total_pixels == 0:
        return
        
    current_pixel = (test_frame * 2) % total_pixels
    brightness = 255
    
    # Convert linear index back to x,y coordinates
    x, y = config.index_to_xy(current_pixel)
    pixel_index = config.xy_to_index(x, y)
    
    try:
        if hasattr(pixels, '__setitem__'):
            pixels[pixel_index] = (brightness, brightness, brightness)
        else:
            pixels[pixel_index] = (brightness, brightness, brightness)
    except IndexError:
        pass

def _test_row_scan(pixels, config, test_frame):
    """Light up one row at a time"""
    if config.matrix_height == 0:
        return
        
    current_row = (test_frame // 5) % config.matrix_height
    brightness = 255
    
    for x in range(config.matrix_width):
        pixel_index = config.xy_to_index(x, current_row)
        try:
            if hasattr(pixels, '__setitem__'):
                pixels[pixel_index] = (brightness, 0, 0)  # Red for rows
            else:
                pixels[pixel_index] = (brightness, 0, 0)
        except IndexError:
            pass

def _test_column_scan(pixels, config, test_frame):
    """Light up one column at a time"""
    if config.matrix_width == 0:
        return
        
    current_column = (test_frame // 5) % config.matrix_width
    brightness = 255
    
    for y in range(config.matrix_height):
        pixel_index = config.xy_to_index(current_column, y)
        try:
            if hasattr(pixels, '__setitem__'):
                pixels[pixel_index] = (0, brightness, 0)  # Green for columns
            else:
                pixels[pixel_index] = (0, brightness, 0)
        except IndexError:
            pass

def _test_wiring_pattern(pixels, config, test_frame):
    """Test to verify serpentine vs progressive wiring"""
    brightness = 255
    
    # Create a checkerboard pattern to make wiring issues obvious
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            # Checkerboard pattern
            if (x + y) % 2 == 0:
                color = (brightness, 0, 0)  # Red
            else:
                color = (0, 0, brightness)  # Blue
            
            pixel_index = config.xy_to_index(x, y)
            try:
                if hasattr(pixels, '__setitem__'):
                    pixels[pixel_index] = (
                        int(max(0, min(255, color[0] * brightness))),
                        int(max(0, min(255, color[1] * brightness))),
                        int(max(0, min(255, color[2] * brightness)))
                    )
                else:
                    pixels[pixel_index] = (
                        int(max(0, min(255, color[0] * brightness))),
                        int(max(0, min(255, color[1] * brightness))),
                        int(max(0, min(255, color[2] * brightness)))
                    )
            except IndexError:
                pass

def _test_corners_edges(pixels, config, test_frame):
    """Test corner and edge pixels"""
    brightness = 255
    
    # Flash corners and edges
    flash = (test_frame // 10) % 2  # Flash every 10 frames
    
    if flash:
        # Light up corners
        corners = [
            (0, 0),  # Top-left
            (config.matrix_width - 1, 0),  # Top-right
            (0, config.matrix_height - 1),  # Bottom-left
            (config.matrix_width - 1, config.matrix_height - 1),  # Bottom-right
        ]
        
        for x, y in corners:
            if 0 <= x < config.matrix_width and 0 <= y < config.matrix_height:
                pixel_index = config.xy_to_index(x, y)
                try:
                    if hasattr(pixels, '__setitem__'):
                        pixels[pixel_index] = (brightness, brightness, 0)  # Yellow
                    else:
                        pixels[pixel_index] = (brightness, brightness, 0)
                except IndexError:
                    pass
        
        # Light up edges
        for x in range(config.matrix_width):
            # Top and bottom edges
            for y in [0, config.matrix_height - 1]:
                if 0 <= y < config.matrix_height:
                    pixel_index = config.xy_to_index(x, y)
                    try:
                        if hasattr(pixels, '__setitem__'):
                            pixels[pixel_index] = (0, brightness, brightness)  # Cyan
                        else:
                            pixels[pixel_index] = (0, brightness, brightness)
                    except IndexError:
                        pass
        
        for y in range(config.matrix_height):
            # Left and right edges
            for x in [0, config.matrix_width - 1]:
                if 0 <= x < config.matrix_width:
                    pixel_index = config.xy_to_index(x, y)
                    try:
                        if hasattr(pixels, '__setitem__'):
                            pixels[pixel_index] = (brightness, 0, brightness)  # Magenta
                        else:
                            pixels[pixel_index] = (brightness, 0, brightness)
                    except IndexError:
                        pass

def _test_gradient(pixels, config, test_frame):
    """Test with color gradients"""
    brightness = 255
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            # Create horizontal gradient (red to blue)
            if config.matrix_width > 1:
                red_intensity = int((1.0 - x / (config.matrix_width - 1)) * 255 * brightness)
                blue_intensity = int((x / (config.matrix_width - 1)) * 255 * brightness)
            else:
                red_intensity = int(255 * brightness)
                blue_intensity = 0
            
            # Add vertical green gradient
            if config.matrix_height > 1:
                green_intensity = int((y / (config.matrix_height - 1)) * 255 * brightness)
            else:
                green_intensity = 0
            
            pixel_index = config.xy_to_index(x, y)
            try:
                if hasattr(pixels, '__setitem__'):
                    pixels[pixel_index] = (
                        int(max(0, min(255, red_intensity * brightness))),
                        int(max(0, min(255, green_intensity * brightness))),
                        int(max(0, min(255, blue_intensity * brightness)))
                    )
                else:
                    pixels[pixel_index] = (
                        int(max(0, min(255, red_intensity * brightness))),
                        int(max(0, min(255, green_intensity * brightness))),
                        int(max(0, min(255, blue_intensity * brightness)))
                    )
            except IndexError:
                pass

# Animation metadata
ANIMATION_INFO = {
    'name': 'Matrix Test',
    'description': 'Hardware verification test patterns',
    'author': 'CosmicLED',
    'version': '1.0',
    'parameters': {
    },
    'features': [
        'All pixels white test',
        'RGB color sweep test',
        'Individual pixel scan',
        'Row and column scanning',
        'Wiring pattern verification',
        'Corner and edge testing',
        'Color gradient test'
    ],
    'usage': 'Run this animation to verify LED matrix wiring and functionality'
}