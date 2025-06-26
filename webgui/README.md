# LightBox Web GUI

A modern, responsive web interface for controlling WS2811/NeoPixel LED matrices with real-time animation control and program management.

## Features

### 🎨 **Animation Control**
- Start/stop animation playback
- Real-time brightness adjustment
- Frame rate control (1-60 FPS)
- Color settings (hue offset, saturation)
- Gamma correction for accurate color reproduction

### 📁 **Program Management**
- Upload custom Python animation scripts via drag & drop
- Browse and switch between available programs
- Delete unwanted programs (except built-in cosmic)
- Real-time program validation and syntax checking

### 💾 **Preset System**
- Save current configuration as named presets
- Load presets with one click
- Delete unwanted presets
- Automatic preset management

### 📊 **Real-time Monitoring**
- Live FPS counter
- Frame count tracking
- System uptime display
- Connection status indicator
- Current program display

### 🎯 **Modern Interface**
- Dark theme with beautiful gradients
- Responsive design for all devices
- Smooth animations and transitions
- Intuitive drag & drop file uploads
- Toast notifications for user feedback

## Usage

### Starting the Web Interface

The web GUI starts automatically when you run the main LightBox application:

```bash
python3 CosmicLED.py
```

The interface will be available at `http://localhost:8080` (or your configured port).

### Uploading Animation Scripts

1. **Drag & Drop**: Simply drag a Python file onto the upload area
2. **Click to Browse**: Click the upload area to select a file from your computer
3. **Validation**: The system automatically validates that your script contains the required `animate(pixels, config, frame)` function

### Creating Animation Scripts

Your Python scripts must follow this format:

```python
def animate(pixels, config, frame):
    """
    Animation function for LED matrix
    
    Args:
        pixels: LED matrix object with __setitem__ method
        config: Configuration object with matrix dimensions and settings
        frame: Current frame number (increments each frame)
    """
    # Your animation code here
    for i in range(len(pixels)):
        # Calculate color for each pixel
        r, g, b = calculate_color(i, frame, config)
        pixels[i] = (r, g, b)
```

### Using Presets

1. **Save Preset**: Adjust your settings, enter a name, and click "Save"
2. **Load Preset**: Click "Load" next to any preset to apply its settings
3. **Delete Preset**: Click the trash icon to remove unwanted presets

## API Endpoints

The web GUI provides a RESTful API for programmatic control:

- `GET /api/status` - Get system status and configuration
- `POST /api/config` - Update configuration settings
- `POST /api/program` - Switch animation program
- `POST /api/upload` - Upload new animation script
- `DELETE /api/delete/<program>` - Delete animation program
- `POST /api/control` - Start/stop animation
- `GET /api/presets` - List available presets
- `POST /api/presets` - Save new preset
- `POST /api/preset/<name>` - Load preset
- `DELETE /api/preset/<name>` - Delete preset

## Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Mobile Support

The interface is fully responsive and works on:
- Smartphones (iOS/Android)
- Tablets
- Desktop computers

## Development

### File Structure

```
webgui/
├── app.py          # Flask application and API endpoints
├── templates/
│   └── index.html  # Main HTML template
├── static/
│   ├── style.css   # Modern CSS styling
│   └── app.js      # JavaScript functionality
└── README.md       # This file
```

### Customization

You can customize the appearance by modifying the CSS variables in `static/style.css`:

```css
:root {
    --primary-color: #6366f1;    /* Main accent color */
    --bg-primary: #0f172a;       /* Background color */
    --text-primary: #f8fafc;     /* Text color */
    /* ... more variables */
}
```

## Troubleshooting

### Connection Issues
- Ensure the LightBox application is running
- Check that the web port (default: 8080) is accessible
- Verify firewall settings allow the connection

### Upload Failures
- Ensure your Python file has the correct `animate()` function signature
- Check that the file is a valid Python script
- Verify the file size is under 5MB

### Performance Issues
- Reduce frame rate if experiencing lag
- Lower brightness to reduce power consumption
- Close other applications to free up system resources

## License

This web GUI is part of the LightBox project and follows the same license terms. 