#!/usr/bin/env python3
"""
LightBox Simulation Mode
Runs LightBox without GPIO dependencies for testing and development
"""

import os
import sys
import traceback

# Set environment variable to force simulation mode
os.environ['LIGHTBOX_SIMULATION'] = '1'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🌟 Starting LightBox in Simulation Mode")
    print("🔧 No GPIO hardware required - perfect for testing!")
    print("🌐 Web interface will be available at http://localhost:8080")
    print("=" * 50)
    
    try:
        # Import here to avoid linter issues
        from Conductor import main
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Simulation stopped by user")
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        traceback.print_exc() 