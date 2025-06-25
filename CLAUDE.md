# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AICheck Integration

Claude should follow the rules specified in `.aicheck/RULES.md` and use AICheck commands:

- `./aicheck action new ActionName` - Create a new action 
- `./aicheck action set ActionName` - Set the current active action
- `./aicheck action complete [ActionName]` - Complete an action with dependency verification
- `./aicheck exec` - Toggle exec mode for system maintenance
- `./aicheck status` - Show the current action status
- `./aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]` - Add external dependency
- `./aicheck dependency internal DEP_ACTION ACTION TYPE [DESCRIPTION]` - Add internal dependency
- `./aicheck auto-iterate` - Start goal-driven AI development cycles (see AUTO_ITERATE_GUIDE.md)

## Project Rules

Claude should follow the rules specified in `.aicheck/RULES.md` with focus on documentation-first approach and adherence to language-specific best practices.

## AICheck Procedures

1. Always check the current action with `./aicheck status` at the start of a session
2. Follow the active action's plan when implementing
3. Create tests before implementation code
4. Document all Claude interactions in supporting_docs/claude-interactions/
5. Only work within the scope of the active action
6. Document all dependencies before completing an action
7. Immediately respond to git hook suggestions before continuing work

## Development Commands

- **Initial setup**: `bash LightBox/setup.sh` (automated installation for Raspberry Pi)
- **Minimal setup**: `bash LightBox/setup-minimal.sh` (for Pi Zero W)
- **Activate environment**: `source LightBox/venv/bin/activate`
- **Run LED controller**: `sudo python3 LightBox/Conductor.py` (requires root for GPIO access)
- **Simulation mode**: `python3 LightBox/run_simulation.py` (development without hardware)
- **Web interface**: Access at <http://localhost:5001> when running (configurable via config.web_port)
- **Install dependencies**: `pip install -r LightBox/requirements.txt` or `pip install -r LightBox/requirements-minimal.txt`
- **Testing**: `pytest` or `python -m pytest tests/` 
- **Hardware test**: `python3 LightBox/scripts/matrix_test.py` to verify LED wiring
- **Production deployment**: Run directly with `sudo python3 LightBox/Conductor.py` (systemd service has permission issues)

## Diagnostic and Debugging Tools

- **GPIO diagnostics**: `python3 LightBox/diagnose_gpio.py` - Check GPIO library conflicts and hardware compatibility
- **General diagnostics**: `python3 LightBox/diagnose.py` - System health and configuration checks
- **LED debugging**: `python3 LightBox/led_debug.py` - Debug LED output and color issues
- **Simple test**: `python3 LightBox/simple_test.py` - Basic LED functionality test

## Architecture Overview

### Core Components

- **Conductor.py**: Main orchestrator that initializes and coordinates all system components including hardware, animation loop, and web interface
- **config.py**: Configuration management with settings persistence, color palettes, and matrix coordinate mapping
- **webgui/app.py**: Flask web interface providing REST API for remote control and real-time monitoring with enhanced program metadata

### Animation System

The project uses a plugin-based animation system:

- Animation programs are Python files in `LightBox/scripts/` with an `animate(pixels, config, frame)` function
- Programs receive pixel array, configuration object, and frame counter
- Built-in animations include: aurora, clouds, feathers, hypnotic_cosmos, matrix_test, cosmic_nebulas, and more
- Dynamic program loading allows hot-swapping animations without restart
- **Animation Function Signature**: `def animate(pixels, config, frame):`
  - `pixels`: RGB array to modify directly (tuple/list format)
  - `config`: Configuration object with matrix dimensions, colors, speed, etc.
  - `frame`: Integer frame counter for timing-based animations
- **Matrix Coordinate Conversion**: Use `config.xy_to_index(x, y)` for 2D positioning
- **Color Validation**: Ensure RGB values are integers 0-255 to avoid "byte range" errors
- **Animation Metadata**: Programs can include `ANIMATION_INFO` dict with metadata for dynamic web GUI controls:
  ```python
  ANIMATION_INFO = {
      'name': 'Display Name',
      'description': 'Brief description of the animation',
      'version': '1.0',
      'author': 'Author Name',
      'parameters': {
          'speed': 'Description of speed parameter (range info)',
          'scale': 'Description of scale parameter (range info)'
      },
      'features': ['List of animation features'],
      'cycle_info': {'timing_details': 'if applicable'}
  }
  ```

### Hardware Integration

- **LED Matrix**: 10x10 WS2811/NeoPixel matrix with serpentine wiring support
- **GPIO Buttons**: Physical controls for mode switching, brightness, and speed (hardware/buttons.py)
- **OLED Display**: Status display integration (hardware/oled.py)
- **Raspberry Pi**: GPIO12 for LED data, various pins for button inputs

### Configuration Management

- **settings.json**: Persistent storage for user preferences
- **Matrix mapping**: xy_to_index() handles serpentine vs progressive wiring patterns
- **Color palettes**: Predefined color schemes with interpolation support
- **Presets**: Save/load complete configuration states

### Web API Architecture

Flask app provides RESTful endpoints:

- `/api/status` - System status and current configuration with program metadata
- `/api/config` - Update animation parameters
- `/api/program` - Switch animation programs
- `/api/program/<name>/info` - Get detailed program information including metadata
- `/api/upload` - Upload new animation scripts
- `/api/palette` - Color palette management
- `/api/presets` - Configuration preset management

### Enhanced Web GUI Features

- **Dynamic Program Information**: Program cards display version, description, author, and features
- **Program Info Modal**: Detailed view showing parameters, features, timing info, and file details
- **Metadata Extraction**: Automatically reads `ANIMATION_INFO` from animation scripts
- **Version Display**: Shows program versions in UI (e.g., "Enhanced Cosmic Nebulas v2.0")

## Dependency Management

When adding external libraries or frameworks:

1. Document with `./aicheck dependency add NAME VERSION JUSTIFICATION`
2. Include specific version requirements
3. Provide clear justification for adding the dependency

When creating dependencies between actions:

1. Document with `./aicheck dependency internal DEP_ACTION ACTION TYPE DESCRIPTION`
2. Specify the type of dependency (data, function, service, etc.)
3. Add detailed description of the dependency relationship

## Claude Workflow

When the user requests work:

1. Check if it fits within the current action (if not, suggest creating a new action)
2. Consult the action plan for guidance
3. Follow test-driven development practices
4. Document your thought process
5. Document all dependencies
6. Implement according to the plan
7. Verify your implementation against the success criteria

## Development Notes

- Animation programs must handle frame-based timing and use config parameters for customization
- Hardware components require root privileges for GPIO access on Raspberry Pi
- Web interface runs on separate thread to avoid blocking LED animation loop
- Matrix coordinate system uses (0,0) at top-left with configurable wiring patterns
- All settings changes are persisted to settings.json automatically
- **Brightness Control**: Uses single `config.brightness` parameter (0.0-1.0) - the old `brightness_scale` parameter has been removed to simplify controls
- **Port Configuration**: Web server port is configurable via `config.web_port` (default 5001) to avoid conflicts with system services
- **Error Handling**: Color values must be in range 0-255; "byte must be in range(0, 256)" errors indicate color calculation issues
- **GPIO Pin Configuration**: LED data pin is GPIO12 (as per hardware setup), uses WS2811/NeoPixel protocol
- **Simulation Mode**: System can run without hardware for development (automatically detected)

## Technology Stack

- **Python 3.11+** - Primary language (checked by setup scripts)
- **Virtual Environment** - Isolated in `LightBox/venv/`
- **Hardware Libraries**: adafruit-blinka, adafruit-circuitpython-neopixel, RPi.GPIO
- **Web Framework**: Flask with CORS support
- **Dependencies**: NumPy (math), Pillow (images), psutil (system monitoring)
- **Package Management**: pyproject.toml with setuptools build system
- **Testing Framework**: pytest with coverage support

## System Integration

- **GPIO Permissions**: Requires root access via sudo for GPIO control
- **Production Deployment**: Run directly with `sudo python3 LightBox/Conductor.py` 
- **SSH Access**: Production Pi accessible at `fieldjoshua@192.168.0.222`
- **Performance**: Optimized for Pi 4, compatible with Pi Zero W (use minimal setup)
- **Service Note**: systemd service has permission issues, use direct sudo execution instead

## Common Issues and Troubleshooting

### Animation Errors
- **"byte must be in range(0, 256)"**: Color values exceeding 0-255 range
  - Check animation calculations that generate RGB values
  - Ensure color interpolation doesn't produce negative or >255 values
  - Use `int()` to convert float calculations to integers
  - Validate color values before assignment: `min(255, max(0, int(value)))`

### Hardware Issues
- **GPIO conflicts**: Run `python3 LightBox/diagnose_gpio.py` to identify library conflicts
- **Permission errors**: Ensure user is in gpio group: `sudo usermod -a -G gpio $USER`
- **LED not responding**: Check wiring and run `python3 LightBox/scripts/matrix_test.py`

### Web Interface Issues
- **Port conflicts**: Default port 5001 configurable via `config.web_port`
- **CORS errors**: Flask app includes CORS support for cross-origin requests
- **Upload failures**: Check file permissions in upload directory
- **Changes not visible**: Restart Conductor.py to reload Flask app changes and new animation metadata

### Production Deployment
- **Start system**: SSH to Pi and run `sudo python3 LightBox/Conductor.py`
- **Stop system**: Use Ctrl+C or kill the process
- **Web GUI access**: Production typically at `http://192.168.0.222:5001`
- **Code deployment**: Changes must be deployed to Pi and system restarted to take effect
- **Service issues**: systemd service has permission problems, use direct execution