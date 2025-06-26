#!/usr/bin/env python3
"""
Animation Test Script - Test individual animations for color range errors
"""

import sys
import importlib.util
from pathlib import Path
import traceback

# Import config
from config import Config

def test_animation(animation_name, frames=10):
    """Test a specific animation for color range errors"""
    print(f"\n🧪 Testing animation: {animation_name}")
    
    # Load the animation
    program_path = Path("scripts") / f"{animation_name}.py"
    if not program_path.exists():
        print(f"❌ Animation file not found: {program_path}")
        return False
    
    try:
        # Load animation module
        spec = importlib.util.spec_from_file_location(animation_name, program_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'animate'):
            print(f"❌ Animation {animation_name} has no animate function")
            return False
            
        print(f"✅ Animation loaded successfully")
        
        # Create test setup
        config = Config()
        pixels = [(0, 0, 0)] * (config.matrix_width * config.matrix_height)
        
        # Test multiple frames
        errors = []
        for frame in range(frames):
            try:
                module.animate(pixels, config, frame)
                
                # Check for invalid values
                invalid_pixels = []
                for i, (r, g, b) in enumerate(pixels):
                    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                        invalid_pixels.append((i, r, g, b))
                
                if invalid_pixels:
                    error_msg = f"Frame {frame}: {len(invalid_pixels)} invalid pixels"
                    if len(invalid_pixels) <= 3:
                        error_msg += f" {invalid_pixels}"
                    errors.append(error_msg)
                    
            except Exception as e:
                errors.append(f"Frame {frame}: Exception - {e}")
        
        if errors:
            print(f"❌ Found {len(errors)} errors:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more errors")
            return False
        else:
            print(f"✅ Animation passed all {frames} frames")
            return True
            
    except Exception as e:
        print(f"❌ Failed to test animation: {e}")
        traceback.print_exc()
        return False

def main():
    """Test all animations or a specific one"""
    if len(sys.argv) > 1:
        # Test specific animation
        animation_name = sys.argv[1]
        frames = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        test_animation(animation_name, frames)
    else:
        # Test all animations
        scripts_dir = Path("scripts")
        animations = [f.stem for f in scripts_dir.glob("*.py") if f.stem != "__pycache__"]
        
        print(f"🔍 Found {len(animations)} animations to test")
        
        passed = []
        failed = []
        
        for animation in sorted(animations):
            if test_animation(animation, 5):  # Test 5 frames each
                passed.append(animation)
            else:
                failed.append(animation)
        
        print(f"\n📊 Test Results:")
        print(f"✅ Passed: {len(passed)} animations")
        for anim in passed:
            print(f"   {anim}")
        
        if failed:
            print(f"❌ Failed: {len(failed)} animations")
            for anim in failed:
                print(f"   {anim}")
        else:
            print("🎉 All animations passed!")

if __name__ == "__main__":
    main()