# LightBox Changelog

All notable changes to the LightBox LED Matrix Animation System are documented here.

## [2.0.0] - 2025-06-25

### ✨ Major Architecture Overhaul
- **Conductor.py**: New main orchestrator replacing CosmicLED.py for better component coordination
- **Enhanced Web GUI**: Program metadata display with version info, descriptions, and features
- **Animation Metadata System**: `ANIMATION_INFO` dict support for dynamic web controls
- **Production Deployment**: Streamlined deployment process with direct sudo execution
- **Comprehensive Documentation**: Updated CLAUDE.md with detailed architecture and troubleshooting

### 🎨 Animation Enhancements
- **Enhanced Cosmic Nebulas v2.0**: Improved particle system with better performance
- **New Animations**: Added zen_garden, organic_flow, symmetry patterns
- **BPM-Synchronized Effects**: Music sync animations (feathers_bpm, plasma_bpm)
- **Animation Versioning**: Version tracking in program metadata
- **Parameter Documentation**: Detailed parameter descriptions in animation info

### 🌐 Web Interface Improvements
- **Program Info Modal**: Detailed program information with metadata display
- **Dynamic Program Cards**: Show version, author, description, and features
- **Enhanced API**: New `/api/program/<name>/info` endpoint for program metadata
- **Real-time Updates**: Improved settings synchronization between web and hardware
- **Responsive Design**: Better mobile compatibility and modern UI

### 🔧 System Improvements
- **Port Configuration**: Configurable web port (default 5001) to avoid macOS conflicts
- **Simulation Mode**: Development mode without hardware requirements
- **GPIO Diagnostics**: Enhanced diagnostic tools for hardware troubleshooting
- **Error Handling**: Better color validation and "byte range" error prevention
- **Performance Optimization**: Frame rate and memory usage improvements for Pi Zero W

### 🛠️ Development Tools
- **Diagnostic Suite**: gpio_diagnose.py, diagnose.py, led_debug.py
- **Testing Framework**: pytest integration with coverage support
- **Setup Scripts**: Automated installation for Pi 4 and Pi Zero W
- **Virtual Environment**: Isolated Python environment in LightBox/venv/
- **Requirements Split**: Full and minimal requirement sets

### 🐛 Bug Fixes
- **Service Permissions**: Resolved systemd service GPIO permission issues
- **Color Range Validation**: Fixed "byte must be in range(0, 256)" errors
- **GPIO Conflicts**: Better detection and resolution of library conflicts
- **Web GUI Sync**: Fixed settings synchronization between interface and hardware
- **Memory Leaks**: Improved memory management in animation loops

### 📚 Documentation
- **Architecture Guide**: Comprehensive system architecture documentation
- **API Reference**: Complete REST API endpoint documentation
- **Troubleshooting**: Common issues and solutions guide
- **Development Workflow**: Setup and development process documentation
- **Production Deployment**: SSH access and deployment procedures

## [1.5.0] - 2025-05-15

### 🎨 Animation System
- **Plugin Architecture**: Dynamic animation loading system
- **Built-in Animations**: aurora, clouds, feathers, hypnotic_cosmos
- **Parameter Control**: Real-time speed, brightness, and color adjustments
- **Preset Management**: Save and recall complete configuration states

### 🌐 Web Interface
- **Flask Integration**: Modern web interface with REST API
- **CORS Support**: Cross-origin request handling
- **Upload System**: Direct animation script upload via web
- **Mobile Responsive**: Touch-friendly controls for mobile devices

### 🔧 Hardware Integration
- **WS2811/NeoPixel Support**: 10x10 LED matrix control
- **GPIO Buttons**: Physical hardware controls
- **OLED Display**: Status display integration
- **Raspberry Pi Optimization**: Performance tuning for Pi hardware

## [1.0.0] - 2025-04-01

### 🚀 Initial Release
- **Basic LED Control**: Single animation with basic controls
- **Configuration System**: JSON-based settings persistence
- **Matrix Mapping**: Serpentine and progressive wiring support
- **Color Palettes**: Predefined color schemes
- **Web Server**: Simple Flask interface for remote control

### 🛠️ Core Features
- **Animation Engine**: Frame-based animation system
- **Color Management**: HSV color space with gamma correction
- **Settings Persistence**: JSON configuration file
- **Hardware Abstraction**: GPIO control with simulation mode
- **Basic Web API**: Status and configuration endpoints

---

## Version Numbering

LightBox follows semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes or architecture overhauls
- **MINOR**: New features and enhancements (backward compatible)
- **PATCH**: Bug fixes and minor improvements

## Upgrade Notes

### 2.0.0 Upgrade
- Replace `CosmicLED.py` calls with `Conductor.py`
- Update web port from 5000 to 5001 if using defaults
- Restart system to load new animation metadata features
- Use direct sudo execution instead of systemd service

### 1.5.0 Upgrade
- Run setup script to install new dependencies
- Update animation scripts to use new plugin interface
- Configure GPIO permissions for hardware access