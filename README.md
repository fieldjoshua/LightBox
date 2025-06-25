# LightBox - LED Matrix Animation System

A sophisticated LED matrix control system for Raspberry Pi with web interface, dynamic animation loading, and real-time parameter control.

## Features

- **10x10 WS2811/NeoPixel LED Matrix** - High-performance animation display
- **Web-Based Control** - Modern responsive interface accessible from any device
- **Dynamic Animation System** - Hot-swappable animation programs with metadata
- **Real-Time Parameter Control** - Live brightness, speed, color, and effect adjustments
- **Hardware Integration** - GPIO buttons, OLED display, and sensor support
- **Preset Management** - Save and recall complete configuration states
- **Production Ready** - Optimized for Raspberry Pi deployment

## Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/fieldjoshua/LightBox.git
cd LightBox

# Run automated setup (Raspberry Pi)
bash LightBox/setup.sh

# Or minimal setup (Pi Zero W)
bash LightBox/setup-minimal.sh
```

### Running the System
```bash
# Activate virtual environment
source LightBox/venv/bin/activate

# Run with hardware (requires sudo for GPIO)
sudo python3 LightBox/Conductor.py

# Or run in simulation mode (development)
python3 LightBox/run_simulation.py
```

### Web Interface
- **Production**: http://192.168.0.222:5001
- **Local Development**: http://localhost:5001

## Architecture

### Core Components
- **Conductor.py** - Main orchestrator coordinating all system components
- **config.py** - Configuration management with settings persistence
- **webgui/app.py** - Flask web interface with REST API
- **scripts/** - Animation programs with plugin architecture

### Animation System
Animation programs are Python files with a simple interface:
```python
def animate(pixels, config, frame):
    # Modify pixels array directly
    # Use config for parameters (brightness, speed, colors)
    # Use frame for timing-based animations
```

Built-in animations include:
- **aurora** - Northern lights simulation
- **cosmic_nebulas** - Deep space particle effects  
- **hypnotic_cosmos** - Mesmerizing spiral patterns
- **plasma_field** - Fluid plasma simulation
- **matrix_test** - Hardware testing and diagnostics

## Hardware Requirements

- **Raspberry Pi 4** (recommended) or Pi Zero W
- **10x10 WS2811/NeoPixel LED Matrix**
- **5V Power Supply** (60W+ recommended)
- **GPIO Connection**: Data pin to GPIO12
- **Optional**: OLED display, control buttons

## API Endpoints

### System Control
- `GET /api/status` - System status and configuration
- `POST /api/config` - Update animation parameters
- `POST /api/program` - Switch animation programs

### Program Management  
- `GET /api/program/<name>/info` - Get program metadata
- `POST /api/upload` - Upload new animation scripts
- `GET /api/presets` - List configuration presets
- `POST /api/presets` - Save/load presets

## Development

### Local Development
```bash
# Install dependencies
pip install -r LightBox/requirements.txt

# Run tests
pytest

# Run simulation mode for development
python3 LightBox/run_simulation.py
```

### Creating Animations
1. Create Python file in `LightBox/scripts/`
2. Implement `animate(pixels, config, frame)` function
3. Add optional `ANIMATION_INFO` metadata dict
4. Upload via web interface or place file directly

### Diagnostics
```bash
# GPIO diagnostics
python3 LightBox/diagnose_gpio.py

# System health check
python3 LightBox/diagnose.py

# LED hardware test
python3 LightBox/scripts/matrix_test.py
```

## Configuration

Key configuration options in `config.py`:
- **Matrix dimensions**: 10x10 (configurable)
- **Web port**: 5001 (configurable via `config.web_port`)
- **GPIO pin**: GPIO12 for LED data
- **Brightness**: 0.0-1.0 scale
- **Frame rate**: Optimized for hardware (15 FPS default)

## Production Deployment

### SSH Access
```bash
ssh fieldjoshua@192.168.0.222
```

### Start/Stop System
```bash
# Start system
sudo python3 LightBox/Conductor.py

# Stop system (Ctrl+C or kill process)
```

### Service Notes
- systemd service has permission issues
- Use direct sudo execution for production
- Changes require system restart to take effect

## Troubleshooting

### Common Issues
- **"byte must be in range(0, 256)"** - Check color calculations in animations
- **GPIO conflicts** - Run `diagnose_gpio.py` to identify library conflicts
- **Permission errors** - Ensure user in gpio group or use sudo
- **LED not responding** - Check wiring and run matrix_test.py

### Performance
- Optimized for Pi 4, compatible with Pi Zero W
- Memory usage monitored and optimized
- Frame rate adjustable based on hardware capabilities

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the animation program interface
4. Test on hardware when possible  
5. Submit a pull request

## Links

- **GitHub**: https://github.com/fieldjoshua/LightBox
- **Web Interface**: http://192.168.0.222:5001
- **Documentation**: See CLAUDE.md for detailed architecture notes