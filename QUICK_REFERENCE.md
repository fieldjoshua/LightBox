# LightBox Quick Reference

## Essential Commands

### System Control
```bash
# Production (requires sudo for GPIO access)
sudo python3 LightBox/Conductor.py

# Development (simulation mode)
python3 LightBox/run_simulation.py

# Activate virtual environment
source LightBox/venv/bin/activate

# Install dependencies
pip install -r LightBox/requirements.txt
pip install -r LightBox/requirements-minimal.txt  # Pi Zero W
```

### Setup and Installation
```bash
# Full setup (Raspberry Pi 4)
bash LightBox/setup.sh

# Minimal setup (Pi Zero W)
bash LightBox/setup-minimal.sh

# SSH to production Pi
ssh fieldjoshua@192.168.0.222
```

### Diagnostics and Testing
```bash
# GPIO diagnostics (hardware conflicts)
python3 LightBox/diagnose_gpio.py

# System health check
python3 LightBox/diagnose.py

# LED debugging
python3 LightBox/led_debug.py

# Hardware test
python3 LightBox/scripts/matrix_test.py

# Run tests
pytest
python -m pytest tests/
```

## Web Interface

### URLs
- **Production**: http://192.168.0.222:5001
- **Local Development**: http://localhost:5001
- **Port Configuration**: Set `config.web_port` in config.py

### Key Features
- Real-time parameter control (brightness, speed, colors)
- Animation program switching with metadata display
- Upload new animation scripts
- Preset management (save/load configurations)
- System status monitoring

## API Endpoints

### Core Control
```bash
# System status
GET /api/status

# Update configuration
POST /api/config
{
  "brightness": 0.8,
  "speed": 1.5,
  "current_program": "aurora"
}

# Switch animation program
POST /api/program
{
  "program": "cosmic_nebulas"
}
```

### Program Management
```bash
# Get program metadata
GET /api/program/<name>/info

# Upload new animation
POST /api/upload
# (multipart form with file)

# List presets
GET /api/presets

# Save/load preset
POST /api/presets
{
  "action": "save",
  "name": "my_preset"
}
```

## Animation Development

### Basic Animation Structure
```python
def animate(pixels, config, frame):
    """
    pixels: RGB array to modify directly [(r,g,b), ...]
    config: Configuration object with matrix dimensions, settings
    frame: Integer frame counter for timing
    """
    for i in range(len(pixels)):
        # Calculate colors based on position and time
        pixels[i] = (red, green, blue)  # Values 0-255
```

### Animation Metadata (Optional)
```python
ANIMATION_INFO = {
    'name': 'My Animation',
    'description': 'Brief description of the animation',
    'version': '1.0',
    'author': 'Your Name',
    'parameters': {
        'speed': 'Animation speed (0.1-3.0)',
        'scale': 'Pattern scale (0.5-2.0)'
    },
    'features': ['Color shifting', 'Smooth transitions'],
    'cycle_info': {'period': '30 seconds', 'seamless': True}
}
```

### Key Functions
```python
# Matrix coordinate conversion
index = config.xy_to_index(x, y)

# Color validation (prevent byte range errors)
r = min(255, max(0, int(red_value)))
g = min(255, max(0, int(green_value)))
b = min(255, max(0, int(blue_value)))

# Configuration access
brightness = config.brightness  # 0.0-1.0
width = config.matrix_width     # 10
height = config.matrix_height   # 10
```

## Configuration

### Key Settings (config.py)
```python
# Matrix hardware
matrix_width = 10
matrix_height = 10
serpentine_wiring = True

# Performance
brightness = 0.5        # 0.0-1.0
fps = 15               # Frame rate
web_port = 5001        # Web interface port

# Animation parameters
speed = 1.0            # Animation speed multiplier
scale = 1.0            # Pattern scale
current_program = "aurora"  # Active animation
```

### Settings Persistence
- **File**: `settings.json` (auto-saved)
- **Web Changes**: Automatically persisted
- **Manual Editing**: Restart system to reload

## Hardware Configuration

### LED Matrix
- **Type**: WS2811/NeoPixel 10x10 matrix
- **Data Pin**: GPIO12 (Raspberry Pi)
- **Power**: 5V 60W+ recommended
- **Wiring**: Serpentine (default) or progressive

### Optional Hardware
- **OLED Display**: SSD1306 for status
- **Buttons**: GPIO inputs for physical control
- **Sensors**: Temperature, motion, etc.

## Troubleshooting

### Common Issues
```bash
# "byte must be in range(0, 256)" error
# → Check animation color calculations, ensure 0-255 range

# GPIO permission denied
# → Use sudo or add user to gpio group
sudo usermod -a -G gpio $USER

# LED matrix not responding
# → Check wiring, run matrix_test.py

# Port 5001 in use
# → Change config.web_port or kill conflicting process

# Animation not loading
# → Check file syntax, restart Conductor.py
```

### Performance Optimization
- **Pi Zero W**: Use minimal requirements, reduce FPS
- **Pi 4**: Full features, higher FPS possible
- **Memory**: Monitor usage, restart if needed
- **Heat**: Ensure adequate cooling for continuous operation

## File Structure

```
LightBox/
├── Conductor.py              # Main system orchestrator
├── config.py                 # Configuration management
├── settings.json             # Persistent settings
├── requirements.txt          # Python dependencies
├── setup.sh                  # Installation script
├── scripts/                  # Animation programs
│   ├── aurora.py
│   ├── cosmic_nebulas.py
│   └── matrix_test.py
├── webgui/                   # Web interface
│   ├── app.py               # Flask application
│   ├── templates/
│   └── static/
├── hardware/                 # Hardware integration
│   ├── buttons.py
│   └── oled.py
├── logs/                     # System logs
└── venv/                     # Virtual environment
```

## Production Workflow

1. **Development**: Work locally with simulation mode
2. **Testing**: Use diagnostic tools and hardware tests
3. **Deployment**: SSH to Pi, update code, restart system
4. **Monitoring**: Check logs and web interface status
5. **Maintenance**: Regular updates and system health checks