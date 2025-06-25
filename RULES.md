# LightBox Development Rules

This document defines the development guidelines and standards for the LightBox LED Matrix Animation System.

> **Quick Navigation**: [Core Principles](#1-core-principles) | [Animation Development](#2-animation-development) | [Web Interface](#3-web-interface-guidelines) | [Hardware Integration](#4-hardware-integration) | [Testing & Deployment](#5-testing-and-deployment) | [Documentation](#6-documentation-standards)

---

## 1. CORE PRINCIPLES

### 1.1 Foundation Rules
- **Safety First** - All electrical connections and GPIO access must be properly managed
- **Real-time Performance** - Animation frame rates must be maintained for smooth visual experience
- **Hardware Compatibility** - Code must work on both Pi 4 and Pi Zero W configurations
- **Production Reliability** - System must run continuously without intervention

### 1.2 System Architecture
The LightBox system consists of:
- **Hardware Layer**: LED matrix, GPIO controls, sensors
- **Animation Engine**: Frame-based rendering with plugin architecture
- **Configuration System**: Persistent settings with real-time updates
- **Web Interface**: Remote control and monitoring
- **Diagnostic Tools**: System health and troubleshooting utilities

**Value Creation**: Smooth, reliable LED animations with intuitive control interfaces.

---

## 2. ANIMATION DEVELOPMENT

### 2.1 Animation Standards
- **Function Signature**: All animations must implement `def animate(pixels, config, frame):`
- **Color Range**: RGB values must be integers in range 0-255
- **Performance**: Animations must complete within frame time budget (67ms for 15 FPS)
- **Error Handling**: Graceful degradation for invalid parameters or calculations

### 2.2 Animation Metadata
```python
ANIMATION_INFO = {
    'name': 'Display Name',                    # Required: Human-readable name
    'description': 'Brief description',        # Required: What the animation does
    'version': '1.0',                         # Required: Semantic version
    'author': 'Author Name',                  # Optional: Creator attribution
    'parameters': {                           # Optional: Parameter descriptions
        'speed': 'Animation speed (0.1-3.0)',
        'scale': 'Pattern scale (0.5-2.0)'
    },
    'features': ['Color shifting', 'Smooth'], # Optional: Key features list
    'cycle_info': {                          # Optional: Timing information
        'period': '30 seconds',
        'seamless': True
    }
}
```

### 2.3 Code Quality Standards
- **Consistent Style**: Follow PEP 8 Python style guidelines
- **Comments**: Explain complex mathematical calculations and algorithms
- **Variable Names**: Use descriptive names (not single letters except for loops)
- **Magic Numbers**: Define constants for key values (wave lengths, frequencies, etc.)

### 2.4 Animation Categories
- **Ambient**: Slow, subtle animations for background mood lighting
- **Dynamic**: Fast-changing patterns with movement and energy
- **Reactive**: Animations that respond to external inputs (music, sensors)
- **Diagnostic**: Testing and calibration animations for hardware validation

---

## 3. WEB INTERFACE GUIDELINES

### 3.1 API Design Principles
- **RESTful Endpoints**: Use standard HTTP methods and status codes
- **JSON Format**: All API requests and responses use JSON
- **Error Handling**: Provide meaningful error messages with proper HTTP status codes
- **CORS Support**: Enable cross-origin requests for development flexibility

### 3.2 Required API Endpoints
```bash
GET  /api/status           # System status and current configuration
POST /api/config           # Update animation parameters
POST /api/program          # Switch animation programs
GET  /api/program/<name>/info  # Get program metadata
POST /api/upload           # Upload new animation scripts
GET  /api/presets          # List configuration presets
POST /api/presets          # Save/load configuration presets
```

### 3.3 User Interface Standards
- **Responsive Design**: Interface must work on mobile devices
- **Real-time Updates**: Settings changes must be immediately visible
- **Visual Feedback**: Loading states and confirmation messages
- **Error Display**: Clear error messages for user actions

### 3.4 Security Requirements
- **Input Validation**: Sanitize all user inputs
- **File Upload Security**: Validate animation script uploads
- **Rate Limiting**: Prevent API abuse
- **Safe Defaults**: Fallback to safe configurations on errors

---

## 4. HARDWARE INTEGRATION

### 4.1 GPIO Management
- **Permission Handling**: Use sudo for GPIO access or proper group membership
- **Pin Configuration**: GPIO12 for LED data, document all pin assignments
- **Conflict Detection**: Check for GPIO library conflicts and provide diagnostics
- **Graceful Degradation**: Simulation mode when hardware is unavailable

### 4.2 LED Matrix Standards
- **Matrix Configuration**: Support 10x10 WS2811/NeoPixel as default
- **Wiring Patterns**: Support both serpentine and progressive wiring
- **Color Correction**: Apply gamma correction for accurate colors
- **Brightness Management**: Enforce safe brightness levels to prevent hardware damage

### 4.3 Power Management
- **Current Limiting**: Monitor and limit LED current draw
- **Thermal Protection**: Implement thermal monitoring if sensors available
- **Safe Shutdown**: Proper GPIO cleanup on system exit
- **Startup Sequence**: Initialize hardware in correct order

### 4.4 Optional Hardware Support
- **OLED Display**: Status information display
- **Physical Buttons**: Hardware controls for common functions
- **Sensors**: Temperature, motion, light sensors for reactive animations
- **Audio Input**: Music synchronization capabilities

---

## 5. TESTING AND DEPLOYMENT

### 5.1 Testing Requirements
- **Unit Tests**: Test configuration management and utility functions
- **Hardware Tests**: Validate LED matrix functionality with test patterns
- **Integration Tests**: Test web API endpoints and animation loading
- **Performance Tests**: Measure frame rates and system resource usage

### 5.2 Diagnostic Tools
```bash
python3 LightBox/diagnose_gpio.py    # GPIO hardware diagnostics
python3 LightBox/diagnose.py         # System health check
python3 LightBox/led_debug.py        # LED output debugging
python3 LightBox/scripts/matrix_test.py  # Hardware test patterns
```

### 5.3 Deployment Standards
- **Environment Isolation**: Use virtual environments for dependencies
- **Service Management**: Direct execution preferred over systemd for GPIO access
- **Monitoring**: Log system performance and errors
- **Backup**: Configuration and animation backup procedures

### 5.4 Production Requirements
- **SSH Access**: Secure remote access for maintenance
- **Log Management**: Rotate logs to prevent disk space issues
- **Update Process**: Safe update procedure without breaking running system
- **Rollback Plan**: Ability to revert to previous working configuration

---

## 6. DOCUMENTATION STANDARDS

### 6.1 Code Documentation
- **Module Docstrings**: Describe purpose and functionality of each Python module
- **Function Documentation**: Parameters, return values, and side effects
- **Inline Comments**: Explain complex algorithms and hardware interactions
- **Type Hints**: Use Python type hints where appropriate

### 6.2 Animation Documentation
- **Parameter Descriptions**: Document all configurable parameters
- **Visual Examples**: Screenshots or videos of animation output when possible
- **Performance Notes**: Frame rate requirements and optimization tips
- **Dependencies**: Note any special requirements or limitations

### 6.3 API Documentation
- **Endpoint Descriptions**: Purpose and usage of each API endpoint
- **Request/Response Examples**: JSON examples for all endpoints
- **Error Codes**: Document possible error conditions and responses
- **Rate Limits**: Any usage restrictions or limitations

### 6.4 Setup Documentation
- **Installation Instructions**: Step-by-step setup for different Pi models
- **Hardware Requirements**: Complete bill of materials and wiring diagrams
- **Configuration Options**: All available settings and their effects
- **Troubleshooting Guide**: Common issues and solutions

---

## 7. FILE ORGANIZATION

### 7.1 Directory Structure
```
LightBox/
├── Conductor.py              # Main system orchestrator
├── config.py                 # Configuration management
├── settings.json             # Runtime settings (not in git)
├── requirements.txt          # Python dependencies
├── requirements-minimal.txt  # Minimal deps for Pi Zero W
├── setup.sh                  # Full installation script
├── setup-minimal.sh          # Minimal installation script
├── scripts/                  # Animation programs
├── webgui/                   # Web interface
├── hardware/                 # Hardware integration modules
├── logs/                     # System logs (not in git)
├── venv/                     # Virtual environment (not in git)
└── tests/                    # Test suite
```

### 7.2 Version Control
- **Git Ignore**: Exclude logs, venv, settings.json, and temporary files
- **Commit Messages**: Descriptive messages following conventional format
- **Branching**: Feature branches for development, master for production
- **Releases**: Tagged releases with semantic versioning

### 7.3 Configuration Management
- **Default Configuration**: Safe defaults in config.py
- **Runtime Settings**: User preferences in settings.json
- **Environment Variables**: System-specific overrides
- **Validation**: Input validation for all configuration parameters

---

## 8. PERFORMANCE STANDARDS

### 8.1 Real-time Requirements
- **Frame Rate**: Maintain consistent 15 FPS minimum
- **Latency**: Web interface changes reflected within 100ms
- **Memory Usage**: Stay within reasonable limits for Pi Zero W
- **CPU Usage**: Leave headroom for system operations

### 8.2 Optimization Guidelines
- **Animation Efficiency**: Minimize calculations per frame
- **Memory Management**: Avoid memory leaks in long-running animations
- **Network Performance**: Minimize API response times
- **Startup Time**: System ready within 30 seconds of boot

### 8.3 Monitoring
- **Performance Metrics**: Track frame rates, memory usage, CPU load
- **Error Tracking**: Log and categorize all system errors
- **Health Checks**: Periodic system health validation
- **Usage Statistics**: Monitor API usage and animation popularity

---

## 9. QUALITY ASSURANCE

### 9.1 Code Review Process
- **Functionality**: Does the code work as intended?
- **Performance**: Will it maintain real-time requirements?
- **Safety**: No risk of hardware damage or system instability?
- **Documentation**: Is the code properly documented?

### 9.2 Testing Process
1. **Static Analysis**: Code style and basic error checking
2. **Unit Tests**: Individual component testing
3. **Integration Tests**: System component interaction
4. **Hardware Tests**: Physical LED matrix validation
5. **Performance Tests**: Real-time requirement validation

### 9.3 Release Criteria
- All tests passing
- Performance benchmarks met
- Documentation updated
- Hardware validation complete
- Production deployment tested

---

**Built for Reliable LED Matrix Control | Hardware Safety | Real-time Performance | Production Ready**