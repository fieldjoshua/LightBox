"""
Flask web application for CosmicLED control panel
Provides REST API and web interface for LED matrix control
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import os
import json
import time
from pathlib import Path
from werkzeug.utils import secure_filename
from config import load_stats

def create_app(matrix=None, config=None):
    """Create Flask application with LED matrix integration"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cosmic-led-secret-key'
    app.config['UPLOAD_FOLDER'] = 'scripts'
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max file size
    
    # Enable CORS for API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Store references to matrix and config
    app.matrix = matrix
    app.config_obj = config
    
    @app.route('/')
    def index():
        """Main web interface"""
        return render_template('index.html')
    
    @app.route('/api/status')
    def api_status():
        """Get system status and current configuration"""
        try:
            # Get runtime stats
            stats = load_stats()
            
            # Get available programs
            programs = []
            scripts_dir = Path('scripts')
            if scripts_dir.exists():
                for script_file in scripts_dir.glob('*.py'):
                    programs.append(script_file.stem)
            
            # Always include built-in cosmic program
            if 'cosmic' not in programs:
                programs.insert(0, 'cosmic')
            
            status = {
                'running': app.matrix.running if app.matrix else False,
                'current_program': app.config_obj.current_program if app.config_obj else 'cosmic',
                'fps': stats.get('fps', 0),
                'frame_count': stats.get('frame_count', 0),
                'uptime': time.time() - stats.get('timestamp', time.time()),
                'programs': programs,
                'config': app.config_obj.get_config_dict() if app.config_obj else {}
            }
            
            return jsonify(status)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config', methods=['GET', 'POST'])
    def api_config():
        """Get or update configuration"""
        if not app.config_obj:
            return jsonify({'error': 'Configuration not available'}), 500
            
        if request.method == 'GET':
            return jsonify(app.config_obj.get_config_dict())
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Update configuration
                updated_fields = []
                
                if 'brightness' in data:
                    app.config_obj.brightness = float(data['brightness'])
                    updated_fields.append('brightness')
                
                if 'gamma' in data:
                    app.config_obj.gamma = float(data['gamma'])
                    updated_fields.append('gamma')
                
                if 'fps' in data:
                    app.config_obj.fps = int(data['fps'])
                    updated_fields.append('fps')
                
                if 'hue_offset' in data:
                    app.config_obj.hue_offset = float(data['hue_offset'])
                    updated_fields.append('hue_offset')
                
                if 'saturation' in data:
                    app.config_obj.saturation = float(data['saturation'])
                    updated_fields.append('saturation')
                
                if 'brightness_scale' in data:
                    app.config_obj.brightness_scale = float(data['brightness_scale'])
                    updated_fields.append('brightness_scale')
                
                if 'speed' in data:
                    app.config_obj.speed = float(data['speed'])
                    updated_fields.append('speed')
                
                if 'scale' in data:
                    app.config_obj.scale = float(data['scale'])
                    updated_fields.append('scale')
                
                if 'current_palette' in data:
                    app.config_obj.current_palette = data['current_palette']
                    updated_fields.append('current_palette')
                
                # Save settings
                app.config_obj.save_settings()
                
                return jsonify({
                    'success': True,
                    'updated_fields': updated_fields,
                    'config': app.config_obj.get_config_dict()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    @app.route('/api/program', methods=['POST'])
    def api_program():
        """Switch animation program"""
        if not app.matrix:
            return jsonify({'error': 'Matrix not available'}), 500
            
        try:
            data = request.get_json()
            if not data or 'program' not in data:
                return jsonify({'error': 'Program name required'}), 400
                
            program_name = data['program']
            
            # Load the program
            app.matrix.load_program(program_name)
            
            return jsonify({
                'success': True,
                'program': program_name
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/upload', methods=['POST'])
    def api_upload():
        """Upload new animation script"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
                
            if file and file.filename.endswith('.py'):
                filename = secure_filename(file.filename)
                
                # Ensure scripts directory exists
                scripts_dir = Path(app.config['UPLOAD_FOLDER'])
                scripts_dir.mkdir(exist_ok=True)
                
                # Save file
                file_path = scripts_dir / filename
                file.save(file_path)
                
                # Validate the script has required animate function
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if 'def animate(' not in content:
                            os.remove(file_path)
                            return jsonify({'error': 'Script must contain animate(pixels, config, frame) function'}), 400
                            
                except Exception as e:
                    if file_path.exists():
                        os.remove(file_path)
                    return jsonify({'error': f'Invalid script: {str(e)}'}), 400
                
                return jsonify({
                    'success': True,  
                    'filename': filename,
                    'program_name': filename[:-3]  # Remove .py extension
                })
            else:
                return jsonify({'error': 'Only Python files (.py) are allowed'}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/palette', methods=['GET', 'POST'])
    def api_palette():
        """Get available palettes or create new one"""
        if not app.config_obj:
            return jsonify({'error': 'Configuration not available'}), 500
            
        if request.method == 'GET':
            return jsonify({
                'palettes': app.config_obj.palettes,
                'current_palette': app.config_obj.current_palette
            })
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data or 'name' not in data or 'colors' not in data:
                    return jsonify({'error': 'Palette name and colors required'}), 400
                    
                name = data['name']
                colors = data['colors']
                
                # Validate colors format
                if not isinstance(colors, list) or len(colors) == 0:
                    return jsonify({'error': 'Colors must be a non-empty list'}), 400
                    
                for color in colors:
                    if not isinstance(color, list) or len(color) != 3:
                        return jsonify({'error': 'Each color must be [r, g, b] format'}), 400
                
                # Add palette
                app.config_obj.palettes[name] = colors
                app.config_obj.save_settings()
                
                return jsonify({
                    'success': True,
                    'palette': name,
                    'colors': colors
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    @app.route('/api/presets', methods=['GET', 'POST'])
    def api_presets():
        """Get available presets or create/load preset"""
        if not app.config_obj:
            return jsonify({'error': 'Configuration not available'}), 500
            
        if request.method == 'GET':
            return jsonify({
                'presets': list(app.config_obj.presets.keys())
            })
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data or 'action' not in data:
                    return jsonify({'error': 'Action required (save or load)'}), 400
                    
                action = data['action']
                
                if action == 'save':
                    if 'name' not in data:
                        return jsonify({'error': 'Preset name required'}), 400
                        
                    name = data['name']
                    app.config_obj.create_preset(name)
                    
                    return jsonify({
                        'success': True,
                        'action': 'saved',
                        'preset': name
                    })
                    
                elif action == 'load':
                    if 'name' not in data:
                        return jsonify({'error': 'Preset name required'}), 400
                        
                    name = data['name']
                    if app.config_obj.load_preset(name):
                        return jsonify({
                            'success': True,
                            'action': 'loaded',
                            'preset': name,
                            'config': app.config_obj.get_config_dict()
                        })
                    else:
                        return jsonify({'error': 'Preset not found'}), 404
                        
                else:
                    return jsonify({'error': 'Invalid action'}), 400
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats')
    def api_stats():
        """Get runtime statistics"""
        try:
            stats = load_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app