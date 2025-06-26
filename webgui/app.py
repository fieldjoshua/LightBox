#!/usr/bin/env python3
"""
LightBox Web GUI - Modern LED Matrix Control Interface
A beautiful, responsive web interface for controlling WS2811/NeoPixel LED matrices
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import time
import threading
from pathlib import Path
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(matrix=None, config=None):
    """Create Flask application with enhanced LED matrix integration"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'lightbox-secret-key-2024'
    app.config['UPLOAD_FOLDER'] = 'scripts'
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
    
    # Enable CORS for all routes
    CORS(app)
    
    # Store references to matrix and config
    app.matrix = matrix
    app.config_obj = config
    
    # Track system state
    app.system_state = {
        'start_time': time.time(),
        'last_activity': time.time(),
        'upload_count': 0,
        'error_count': 0
    }
    
    def get_system_info():
        """Get comprehensive system information"""
        try:
            stats = {}
            if hasattr(config, 'load_stats'):
                loaded_stats = config.load_stats()
                # Ensure stats is a dictionary, not a list
                if isinstance(loaded_stats, dict):
                    stats = loaded_stats
                else:
                    logger.warning(f"load_stats returned non-dict type: {type(loaded_stats)}")
                    stats = {}
            
            programs = []
            scripts_dir = Path('scripts')
            if scripts_dir.exists():
                for script_file in scripts_dir.glob('*.py'):
                    if script_file.name != '__init__.py':
                        program_info = {
                            'name': script_file.stem,
                            'size': script_file.stat().st_size,
                            'modified': datetime.fromtimestamp(script_file.stat().st_mtime).isoformat()
                        }
                        
                        # Try to extract ANIMATION_INFO metadata
                        try:
                            with open(script_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Simple extraction of ANIMATION_INFO dict
                                if 'ANIMATION_INFO' in content:
                                    # Execute the module to extract metadata safely
                                    import importlib.util
                                    spec = importlib.util.spec_from_file_location(script_file.stem, script_file)
                                    module = importlib.util.module_from_spec(spec)
                                    spec.loader.exec_module(module)
                                    
                                    if hasattr(module, 'ANIMATION_INFO'):
                                        program_info['metadata'] = module.ANIMATION_INFO
                        except Exception as e:
                            logger.debug(f"Could not extract metadata from {script_file.name}: {e}")
                        
                        programs.append(program_info)
            
            # Sort programs by name
            programs.sort(key=lambda x: x['name'])
            
            uptime = time.time() - app.system_state['start_time']
            
            # Get config dict safely
            config_dict = {}
            if app.config_obj:
                try:
                    config_result = app.config_obj.get_config_dict()
                    if isinstance(config_result, dict):
                        config_dict = config_result
                    else:
                        logger.warning(f"get_config_dict returned non-dict type: {type(config_result)}")
                        config_dict = {}
                except Exception as e:
                    logger.error(f"Error getting config dict: {e}")
                    config_dict = {}

            return {
                'running': app.matrix.running if app.matrix else False,
                'current_program': app.config_obj.current_program if app.config_obj else 'cosmic',
                'fps': stats.get('fps', 0),
                'frame_count': stats.get('frame_count', 0),
                'uptime': uptime,
                'uptime_formatted': format_uptime(uptime),
                'programs': programs,
                'config': config_dict,
                'system': {
                    'start_time': datetime.fromtimestamp(app.system_state['start_time']).isoformat(),
                    'last_activity': datetime.fromtimestamp(app.system_state['last_activity']).isoformat(),
                    'upload_count': app.system_state['upload_count'],
                    'error_count': app.system_state['error_count']
                }
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {'error': str(e)}
    
    def format_uptime(seconds):
        """Format uptime in human readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"
    
    @app.route('/')
    def index():
        """Main web interface"""
        return render_template('index.html')
    
    @app.route('/api/status')
    def api_status():
        """Get system status and current configuration"""
        try:
            app.system_state['last_activity'] = time.time()
            return jsonify(get_system_info())
        except Exception as e:
            app.system_state['error_count'] += 1
            logger.error(f"Status API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config', methods=['GET', 'POST'])
    def api_config():
        """Get or update configuration"""
        if not app.config_obj:
            return jsonify({'error': 'Configuration not available'}), 500
        
        app.system_state['last_activity'] = time.time()
        
        if request.method == 'GET':
            return jsonify(app.config_obj.get_config_dict())
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Update configuration
                updated_fields = []
                config_updates = {}
                
                # Define valid config fields and their types
                config_fields = {
                    'brightness': float,
                    'gamma': float,
                    'fps': int,
                    'hue_offset': float,
                    'saturation': float,
                    'speed': float,
                    'scale': float,
                    'current_palette': str
                }
                
                for field, field_type in config_fields.items():
                    if field in data:
                        try:
                            value = field_type(data[field])
                            setattr(app.config_obj, field, value)
                            updated_fields.append(field)
                            config_updates[field] = value
                        except (ValueError, TypeError) as e:
                            return jsonify({'error': f'Invalid {field}: {e}'}), 400
                
                # Save settings
                app.config_obj.save_settings()
                
                # Mark config as updated for real-time detection
                app.config_obj.mark_updated()
                
                # Update hardware immediately
                try:
                    if (app.matrix and app.matrix.pixels and 
                        hasattr(app.matrix.pixels, 'brightness') and 
                        'brightness' in config_updates):
                        app.matrix.pixels.brightness = config_updates['brightness']
                except Exception as e:
                    logger.warning(f"Failed to update hardware brightness: {e}")
                
                return jsonify({
                    'success': True,
                    'updated_fields': updated_fields,
                    'config': app.config_obj.get_config_dict()
                })
                
            except Exception as e:
                app.system_state['error_count'] += 1
                logger.error(f"Config API error: {e}")
                return jsonify({'error': str(e)}), 500
    
    @app.route('/api/program', methods=['POST'])
    def api_program():
        """Switch animation program"""
        if not app.matrix:
            return jsonify({'error': 'Matrix not available'}), 500
        
        app.system_state['last_activity'] = time.time()
        
        try:
            data = request.get_json()
            if not data or 'program' not in data:
                return jsonify({'error': 'Program name required'}), 400
            
            program_name = data['program']
            
            # Load the program
            app.matrix.load_program(program_name)
            
            return jsonify({
                'success': True,
                'program': program_name,
                'message': f'Switched to {program_name}'
            })
            
        except Exception as e:
            app.system_state['error_count'] += 1
            logger.error(f"Program API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/program/<program_name>/info')
    def api_program_info(program_name):
        """Get detailed information about a specific program including metadata"""
        app.system_state['last_activity'] = time.time()
        
        try:
            script_path = Path('scripts') / f"{program_name}.py"
            if not script_path.exists():
                return jsonify({'error': 'Program not found'}), 404
            
            program_info = {
                'name': program_name,
                'size': script_path.stat().st_size,
                'modified': datetime.fromtimestamp(script_path.stat().st_mtime).isoformat(),
                'is_current': app.config_obj.current_program == program_name if app.config_obj else False
            }
            
            # Extract ANIMATION_INFO metadata
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(program_name, script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'ANIMATION_INFO'):
                    program_info['metadata'] = module.ANIMATION_INFO
                else:
                    program_info['metadata'] = {
                        'name': program_name.replace('_', ' ').title(),
                        'description': 'Custom animation program',
                        'version': '1.0',
                        'parameters': {
                            'speed': 'Animation speed (0.1-3.0)',
                            'scale': 'Pattern scale (0.5-3.0)',
                            'hue_offset': 'Color shift (0-360 degrees)',
                            'saturation': 'Color saturation (0.0-1.0)',
                            'brightness': 'Overall brightness (0.0-1.0)'
                        }
                    }
            except Exception as e:
                logger.debug(f"Could not extract metadata from {program_name}: {e}")
                program_info['metadata'] = {
                    'name': program_name.replace('_', ' ').title(),
                    'description': 'Animation program',
                    'version': 'Unknown',
                    'parameters': {}
                }
            
            return jsonify(program_info)
            
        except Exception as e:
            app.system_state['error_count'] += 1
            logger.error(f"Program info API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/upload', methods=['POST'])
    def api_upload():
        """Upload new animation script"""
        app.system_state['last_activity'] = time.time()
        
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.endswith('.py'):
                return jsonify({'error': 'Only Python (.py) files are allowed'}), 400
            
            filename = secure_filename(file.filename)
            
            # Ensure scripts directory exists
            scripts_dir = Path(app.config['UPLOAD_FOLDER'])
            scripts_dir.mkdir(exist_ok=True)
            
            # Save file
            file_path = scripts_dir / filename
            file.save(file_path)
            
            # Validate the script
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Check for required animate function
                    if 'def animate(' not in content:
                        os.remove(file_path)
                        return jsonify({
                            'error': 'Script must contain animate(pixels, config, frame) function'
                        }), 400
                    
                    # Check for basic syntax
                    compile(content, filename, 'exec')
                    
            except SyntaxError as e:
                if file_path.exists():
                    os.remove(file_path)
                return jsonify({'error': f'Syntax error: {str(e)}'}), 400
            except Exception as e:
                if file_path.exists():
                    os.remove(file_path)
                return jsonify({'error': f'Invalid script: {str(e)}'}), 400
            
            app.system_state['upload_count'] += 1
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': f'Successfully uploaded {filename}'
            })
            
        except Exception as e:
            app.system_state['error_count'] += 1
            logger.error(f"Upload API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/delete/<program_name>', methods=['DELETE'])
    def api_delete_program(program_name):
        """Delete an animation program"""
        app.system_state['last_activity'] = time.time()
        
        try:
            if program_name == 'cosmic':
                return jsonify({'error': 'Cannot delete built-in cosmic program'}), 400
            
            script_path = Path('scripts') / f"{program_name}.py"
            
            if not script_path.exists():
                return jsonify({'error': 'Program not found'}), 404
            
            # Check if it's currently running
            if (app.config_obj and app.config_obj.current_program == program_name):
                return jsonify({'error': 'Cannot delete currently running program'}), 400
            
            os.remove(script_path)
            
            return jsonify({
                'success': True,
                'message': f'Deleted {program_name}'
            })
            
        except Exception as e:
            app.system_state['error_count'] += 1
            logger.error(f"Delete API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/control', methods=['POST'])
    def api_control():
        """Control animation (start/stop)"""
        if not app.matrix:
            return jsonify({'error': 'Matrix not available'}), 500
        
        app.system_state['last_activity'] = time.time()
        
        try:
            data = request.get_json()
            if not data or 'action' not in data:
                return jsonify({'error': 'Action required'}), 400
            
            action = data['action']
            
            if action == 'start':
                if not app.matrix.running:
                    # Start animation in background thread
                    def start_animation():
                        try:
                            app.matrix.start()
                        except Exception as e:
                            logger.error(f"Animation error: {e}")
                    
                    thread = threading.Thread(target=start_animation, daemon=True)
                    thread.start()
                
                return jsonify({
                    'success': True,
                    'message': 'Animation started'
                })
            
            elif action == 'stop':
                if app.matrix.running:
                    app.matrix.stop()
                
                return jsonify({
                    'success': True,
                    'message': 'Animation stopped'
                })
            
            else:
                return jsonify({'error': 'Invalid action'}), 400
                
        except Exception as e:
            app.system_state['error_count'] += 1
            logger.error(f"Control API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/palette', methods=['GET', 'POST'])
    def api_palette():
        """Get or update color palette"""
        if not app.config_obj:
            return jsonify({'error': 'Configuration not available'}), 500
        
        app.system_state['last_activity'] = time.time()
        
        if request.method == 'GET':
            return jsonify({
                'current_palette': app.config_obj.current_palette,
                'available_palettes': app.config_obj.get_available_palettes()
            })
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data or 'palette' not in data:
                    return jsonify({'error': 'Palette name required'}), 400
                
                palette_name = data['palette']
                app.config_obj.current_palette = palette_name
                app.config_obj.save_settings()
                app.config_obj.mark_updated()
                
                return jsonify({
                    'success': True,
                    'palette': palette_name
                })
                
            except Exception as e:
                app.system_state['error_count'] += 1
                logger.error(f"Palette API error: {e}")
                return jsonify({'error': str(e)}), 500
    
    @app.route('/api/presets', methods=['GET', 'POST'])
    def api_presets():
        """Get or save configuration presets"""
        if not app.config_obj:
            return jsonify({'error': 'Configuration not available'}), 500
        
        app.system_state['last_activity'] = time.time()
        
        presets_file = Path('presets.json')
        
        if request.method == 'GET':
            try:
                if presets_file.exists():
                    with open(presets_file, 'r') as f:
                        presets = json.load(f)
                else:
                    presets = {}
                
                return jsonify(presets)
                
            except Exception as e:
                logger.error(f"Presets GET error: {e}")
                return jsonify({'error': str(e)}), 500
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data or 'name' not in data:
                    return jsonify({'error': 'Preset name required'}), 400
                
                preset_name = data['name']
                preset_config = data.get('config', app.config_obj.get_config_dict())
                
                # Load existing presets
                if presets_file.exists():
                    with open(presets_file, 'r') as f:
                        presets = json.load(f)
                else:
                    presets = {}
                
                # Save new preset
                presets[preset_name] = {
                    'config': preset_config,
                    'created': datetime.now().isoformat()
                }
                
                with open(presets_file, 'w') as f:
                    json.dump(presets, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'preset': preset_name
                })
                
            except Exception as e:
                app.system_state['error_count'] += 1
                logger.error(f"Presets POST error: {e}")
                return jsonify({'error': str(e)}), 500
    
    @app.route('/api/preset/<preset_name>', methods=['POST', 'DELETE'])
    def api_preset(preset_name):
        """Load or delete a specific preset"""
        if not app.config_obj:
            return jsonify({'error': 'Configuration not available'}), 500
        
        app.system_state['last_activity'] = time.time()
        
        presets_file = Path('presets.json')
        
        try:
            if not presets_file.exists():
                return jsonify({'error': 'No presets found'}), 404
            
            with open(presets_file, 'r') as f:
                presets = json.load(f)
            
            if preset_name not in presets:
                return jsonify({'error': 'Preset not found'}), 404
            
            if request.method == 'POST':
                # Load preset
                preset_config = presets[preset_name]['config']
                
                # Apply configuration
                for key, value in preset_config.items():
                    if hasattr(app.config_obj, key):
                        setattr(app.config_obj, key, value)
                
                app.config_obj.save_settings()
                app.config_obj.mark_updated()
                
                return jsonify({
                    'success': True,
                    'preset': preset_name,
                    'config': app.config_obj.get_config_dict()
                })
            
            elif request.method == 'DELETE':
                # Delete preset
                del presets[preset_name]
                
                with open(presets_file, 'w') as f:
                    json.dump(presets, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'message': f'Deleted preset {preset_name}'
                })
                
        except Exception as e:
            app.system_state['error_count'] += 1
            logger.error(f"Preset API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats')
    def api_stats():
        """Get detailed system statistics"""
        try:
            stats = {}
            if hasattr(config, 'load_stats'):
                stats = config.load_stats()
            
            return jsonify({
                'runtime_stats': stats,
                'system_stats': app.system_state,
                'matrix_info': {
                    'running': app.matrix.running if app.matrix else False,
                    'current_program': app.config_obj.current_program if app.config_obj else None,
                    'frame_count': getattr(app.matrix, 'frame_count', 0) if app.matrix else 0,
                    'current_fps': getattr(app.matrix, 'current_fps', 0) if app.matrix else 0
                }
            })
            
        except Exception as e:
            app.system_state['error_count'] += 1
            logger.error(f"Stats API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health')
    def api_health():
        """Health check endpoint for monitoring and load balancers"""
        try:
            import psutil
            import os
            
            # Get system health metrics
            uptime = time.time() - app.system_state['start_time']
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Check matrix status
            matrix_healthy = app.matrix and app.matrix.running if app.matrix else False
            
            # Check if we have recent frame updates (matrix is actually working)
            recent_frames = False
            if app.matrix:
                recent_frames = getattr(app.matrix, 'frame_count', 0) > 0
            
            # Check for GPIO access
            gpio_available = os.path.exists('/dev/gpiomem') or os.path.exists('/dev/mem')
            
            # Determine overall health status
            is_healthy = (
                matrix_healthy and
                recent_frames and
                memory_percent < 90 and
                cpu_percent < 95 and
                app.system_state['error_count'] < 10
            )
            
            health_data = {
                'status': 'healthy' if is_healthy else 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': uptime,
                'uptime_formatted': format_uptime(uptime),
                'matrix': {
                    'running': matrix_healthy,
                    'has_frames': recent_frames,
                    'current_program': app.config_obj.current_program if app.config_obj else None,
                    'frame_count': getattr(app.matrix, 'frame_count', 0) if app.matrix else 0,
                    'fps': getattr(app.matrix, 'current_fps', 0) if app.matrix else 0
                },
                'system': {
                    'memory_percent': memory_percent,
                    'cpu_percent': cpu_percent,
                    'gpio_available': gpio_available,
                    'error_count': app.system_state['error_count']
                },
                'thresholds': {
                    'memory_warning': 80,
                    'memory_critical': 90,
                    'cpu_warning': 80,
                    'cpu_critical': 95,
                    'error_limit': 10
                }
            }
            
            # Return appropriate HTTP status code
            status_code = 200 if is_healthy else 503
            return jsonify(health_data), status_code
            
        except ImportError:
            # psutil not available, basic health check
            basic_health = {
                'status': 'limited',
                'timestamp': datetime.now().isoformat(),
                'message': 'psutil not available for detailed system metrics',
                'matrix': {
                    'running': app.matrix.running if app.matrix else False,
                    'current_program': app.config_obj.current_program if app.config_obj else None
                }
            }
            return jsonify(basic_health), 200
            
        except Exception as e:
            app.system_state['error_count'] += 1
            logger.error(f"Health check error: {e}")
            return jsonify({
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }), 500
    
    @app.route('/api/logs')
    def api_logs():
        """Get recent system logs"""
        try:
            # This would typically read from a log file
            # For now, return basic system info
            return jsonify({
                'logs': [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'level': 'INFO',
                        'message': 'System running normally'
                    }
                ]
            })
        except Exception as e:
            logger.error(f"Logs API error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.system_state['error_count'] += 1
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app