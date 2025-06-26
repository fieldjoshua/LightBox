#!/usr/bin/env python3
"""
Standalone Web Interface Starter
Runs the web interface separately from the LED controller for stability
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    try:
        from config import Config
        from webgui.app import create_app
        
        print("🌐 Starting LightBox Web Interface...")
        
        # Initialize configuration
        config = Config()
        
        # Create app without matrix reference (file-based sync)
        app = create_app(None, config)
        
        print(f"🚀 Web interface starting on port {config.web_port}")
        print(f"🌐 Local access: http://localhost:{config.web_port}")
        print(f"🌐 Network access: http://192.168.0.222:{config.web_port}")
        print("📝 Settings changes will be saved to settings.json")
        print("🔄 Restart LED service to apply changes: sudo systemctl restart lightbox.service")
        
        # Run web server
        app.run(
            host='0.0.0.0',
            port=config.web_port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        print("\n⏹️  Web interface stopped")
    except Exception as e:
        print(f"❌ Web interface error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()