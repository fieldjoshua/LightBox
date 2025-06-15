# 🌟 CosmicLED - LED Matrix Animation System

A comprehensive Raspberry Pi-based LED matrix animation system with web control interface, supporting WS2811/NeoPixel LED strips with hot-swappable animation programs.

## Features

- **LED Matrix Control**: Support for WS2811/NeoPixel LED matrices with configurable wiring patterns
- **Web Interface**: Real-time control panel accessible via web browser
- **Hot-Swappable Animations**: Load new animation programs without restarting
- **Hardware Integration**: GPIO button controls and OLED status display
- **Persistent Settings**: Save/load configuration presets
- **Animation Library**: Built-in cosmic animation plus uploadable custom programs
- **Real-time Statistics**: FPS monitoring and system status tracking

## Hardware Requirements

- **Raspberry Pi 4** (recommended) or Pi 3B+ with Raspberry Pi OS (Bookworm)
- **LED Matrix**: WS2811/WS2812B/NeoPixel compatible LED strip arranged in matrix
- **Power Supply**: Adequate 5V power supply for LED matrix (calculate ~60mA per LED)
- **Level Shifter**: 3.3V to 5V logic level shifter for reliable data signal
- **Optional**: GPIO buttons for physical controls, OLED display for status

## Quick Start

### 1. Hardware Setup

Connect your LED matrix to the Raspberry Pi:
- **Data**: LED data input to GPIO18 (pin 12) via level shifter
- **Power**: 5V and GND from external power supply
- **Ground**: Common ground between Pi and LED power supply

### 2. Software Installation

```bash
# Clone or download the LightBox project
cd LightBox

# Run setup script (requires sudo for GPIO permissions)
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 3. Configuration

Edit the matrix settings in `config.py` or use the web interface:
- **Matrix size**: Set `matrix_width` and `matrix_height`
- **Wiring pattern**: Set `serpentine_wiring` (True for snake pattern, False for progressive)
- **GPIO pin**: Default is GPIO18, change in `CosmicLED.py` if needed

### 4. Launch

```bash
# Start the LED matrix system (requires sudo for GPIO access)
sudo ./venv/bin/python3 CosmicLED.py
```

Access the web interface at: `http://your-pi-ip:5000`

## Web Interface

The control panel provides:

- **Program Selection**: Switch between animation programs
- **Brightness Control**: Adjust LED brightness with gamma correction
- **Color Settings**: Choose color palettes and adjust hue/saturation
- **Animation Parameters**: Control speed, scale, and intensity
- **Preset Management**: Save and load configuration presets
- **Upload Programs**: Upload new Python animation scripts
- **Live Statistics**: Monitor FPS, frame count, and system status

## Creating Custom Animations

Animation programs are Python files in the `scripts/` directory with an `animate()` function:

```python
def animate(pixels, config, frame):
    \"\"\"
    Custom animation function
    
    Args:
        pixels: LED pixel array to modify
        config: Configuration object with matrix settings
        frame: Current frame number
    \"\"\"
    
    for y in range(config.matrix_height):
        for x in range(config.matrix_width):
            # Calculate color for this pixel
            r, g, b = calculate_color(x, y, frame)
            
            # Set pixel color
            pixel_index = config.xy_to_index(x, y)
            pixels[pixel_index] = (r, g, b)
```

### Available Configuration Parameters

- `config.matrix_width/height`: Matrix dimensions
- `config.brightness`: Overall brightness (0.0-1.0)
- `config.speed`: Animation speed multiplier
- `config.scale`: Pattern scale multiplier
- `config.hue_offset`: Color hue shift (0-360°)
- `config.saturation`: Color saturation (0.0-1.0)
- `config.current_palette`: Active color palette name
- `config.get_palette_color(position)`: Get color from palette
- `config.hsv_to_rgb(h, s, v)`: Convert HSV to RGB
- `config.xy_to_index(x, y)`: Convert coordinates to pixel index

## Built-in Animations

### Cosmic (Default)
Flowing cosmic colors with wave patterns

### Shimmer  
Shimmering wave effect with sparkles

### Symmetry
Symmetrical patterns with radial and mirror effects

### Matrix Test
Hardware verification animation for testing LED wiring

## Hardware Integration

### GPIO Buttons (Optional)

Connect buttons to these GPIO pins (BCM numbering):
- **Pin 21**: Brightness control (single press: increase, double press: decrease)
- **Pin 20**: Program switching (cycles through available programs)
- **Pin 16**: Speed control (single press: increase, double press: decrease)
- **Pin 12**: Preset cycling (loads next preset)

Long press actions:
- **Brightness**: Reset to 50%
- **Program**: Reload current program
- **Speed**: Reset to 1.0x
- **Preset**: Save current settings as 'Quick' preset

### OLED Display (Optional)

Connect a 128x64 SSD1306 OLED display via I2C:
- **SDA**: GPIO2 (pin 3)
- **SCL**: GPIO3 (pin 5)
- **VCC**: 3.3V
- **GND**: Ground

The display cycles through status screens showing:
1. System status and FPS
2. Current program and matrix info
3. Settings (brightness, speed, palette)
4. System statistics (uptime, memory, temperature)

## Auto-Start on Boot

Enable the systemd service to start CosmicLED automatically:

```bash
# Copy service file (created by setup.sh)
sudo cp lightbox.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable lightbox.service
sudo systemctl start lightbox.service

# Check status
sudo systemctl status lightbox.service
```

## Configuration Files

### settings.json
Persistent configuration storage:
```json
{
  \"matrix_width\": 10,
  \"matrix_height\": 10,
  \"serpentine_wiring\": true,
  \"brightness\": 0.5,
  \"current_program\": \"cosmic\",
  \"current_palette\": \"rainbow\",
  \"presets\": {
    \"Bright\": { \"brightness\": 0.8, \"speed\": 1.5 },
    \"Dim\": { \"brightness\": 0.2, \"speed\": 0.8 }
  }
}
```

### Runtime Statistics
Live statistics are saved to `/tmp/cosmic_stats.json`:
```json
{
  \"fps\": 30,
  \"frame_count\": 1234,
  \"program\": \"cosmic\",
  \"brightness\": 0.5,
  \"timestamp\": 1640995200
}
```

## Troubleshooting

### Common Issues

**LEDs not lighting up:**
- Check power supply capacity (60mA per LED)
- Verify GPIO18 connection and level shifter
- Ensure common ground between Pi and LED power
- Test with `matrix_test.py` animation

**Wrong colors/patterns:**
- Check `serpentine_wiring` setting in config
- Verify matrix dimensions match actual hardware
- Test with hardware verification animation

**Permission errors:**
- Run with `sudo` for GPIO access  
- Add user to `gpio` group: `sudo usermod -a -G gpio $USER`

**Web interface not accessible:**
- Check if port 5000 is blocked by firewall
- Verify Pi's IP address
- Check for port conflicts with other services

### Performance Optimization

- **Reduce FPS**: Lower frame rate if Pi is struggling
- **Optimize animations**: Avoid complex calculations in animation loops
- **Power management**: Use adequate power supply to prevent voltage drops
- **Heat management**: Ensure proper Pi cooling for sustained operation

### Debug Mode

Run with verbose output:
```bash
sudo ./venv/bin/python3 CosmicLED.py --debug
```

## API Reference

### REST Endpoints

- `GET /api/status` - System status and configuration
- `GET /api/config` - Current configuration
- `POST /api/config` - Update configuration
- `POST /api/program` - Switch animation program
- `POST /api/upload` - Upload new animation script
- `GET /api/palette` - Available color palettes
- `POST /api/palette` - Create new color palette
- `GET /api/presets` - Available presets
- `POST /api/presets` - Save/load presets
- `GET /api/stats` - Runtime statistics

## Contributing

1. Fork the repository
2. Create animation programs in `scripts/` directory
3. Test with `matrix_test.py` animation
4. Submit pull request with documentation

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check troubleshooting section above
- Review hardware connections
- Test with built-in animations first
- Verify power supply capacity

---

**SSH Access**: For remote management: `ssh fieldjoshua@192.168.0.222`

*Created with ❤️ for the maker community*
