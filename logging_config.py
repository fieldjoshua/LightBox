#!/usr/bin/env python3
"""
LightBox Logging Configuration - Comprehensive logging setup for production
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime

class LightBoxLogger:
    """Centralized logging configuration for LightBox system"""
    
    def __init__(self, log_dir="logs", max_size_mb=10, backup_count=5):
        self.log_dir = Path(log_dir)
        self.max_size_mb = max_size_mb
        self.backup_count = backup_count
        self.loggers = {}
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup main application logger
        self.setup_main_logger()
        
    def setup_main_logger(self):
        """Setup the main application logger"""
        main_logger = logging.getLogger('lightbox')
        main_logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        main_logger.handlers.clear()
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        main_logger.addHandler(console_handler)
        
        # File handler for persistent logging
        log_file = self.log_dir / "lightbox.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_size_mb * 1024 * 1024,
            backupCount=self.backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        main_logger.addHandler(file_handler)
        
        # Store reference
        self.loggers['main'] = main_logger
        
        return main_logger
    
    def setup_component_logger(self, component_name, level=logging.INFO):
        """Setup logger for specific component (animation, web, hardware, etc.)"""
        logger_name = f'lightbox.{component_name}'
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Component-specific log file
        log_file = self.log_dir / f"{component_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_size_mb * 1024 * 1024,
            backupCount=self.backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Detailed formatter for component logs
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Store reference
        self.loggers[component_name] = logger
        
        return logger
    
    def setup_error_logger(self):
        """Setup dedicated error logger for critical issues"""
        error_logger = logging.getLogger('lightbox.errors')
        error_logger.setLevel(logging.ERROR)
        
        # Clear any existing handlers
        error_logger.handlers.clear()
        
        # Error-specific log file
        log_file = self.log_dir / "errors.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_size_mb * 1024 * 1024,
            backupCount=self.backup_count
        )
        file_handler.setLevel(logging.ERROR)
        
        # Detailed error formatter
        error_formatter = logging.Formatter(
            '%(asctime)s - CRITICAL - %(name)s - %(funcName)s:%(lineno)d\n'
            'Error: %(message)s\n'
            'Process: %(process)d | Thread: %(thread)d\n'
            '%(pathname)s:%(lineno)d\n' + '-' * 50,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(error_formatter)
        error_logger.addHandler(file_handler)
        
        # Also send errors to console
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.ERROR)
        console_formatter = logging.Formatter(
            '❌ %(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        error_logger.addHandler(console_handler)
        
        # Store reference
        self.loggers['errors'] = error_logger
        
        return error_logger
    
    def setup_performance_logger(self):
        """Setup performance metrics logger"""
        perf_logger = logging.getLogger('lightbox.performance')
        perf_logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        perf_logger.handlers.clear()
        
        # Performance log file
        log_file = self.log_dir / "performance.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_size_mb * 1024 * 1024,
            backupCount=self.backup_count
        )
        file_handler.setLevel(logging.INFO)
        
        # CSV-like formatter for easy parsing
        perf_formatter = logging.Formatter(
            '%(asctime)s,%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(perf_formatter)
        perf_logger.addHandler(file_handler)
        
        # Store reference
        self.loggers['performance'] = perf_logger
        
        return perf_logger
    
    def get_logger(self, component='main'):
        """Get logger for specified component"""
        if component not in self.loggers:
            if component == 'errors':
                return self.setup_error_logger()
            elif component == 'performance':
                return self.setup_performance_logger()
            else:
                return self.setup_component_logger(component)
        
        return self.loggers[component]
    
    def log_startup(self, version="1.0", config_summary=None):
        """Log system startup information"""
        main_logger = self.get_logger('main')
        main_logger.info("=" * 60)
        main_logger.info(f"🌟 LightBox LED Matrix System Starting - v{version}")
        main_logger.info(f"📅 Startup time: {datetime.now().isoformat()}")
        main_logger.info(f"🖥️  Python: {sys.version}")
        main_logger.info(f"📁 Working directory: {os.getcwd()}")
        
        if config_summary:
            main_logger.info("⚙️  Configuration:")
            for key, value in config_summary.items():
                main_logger.info(f"   {key}: {value}")
        
        main_logger.info("=" * 60)
    
    def log_shutdown(self):
        """Log system shutdown"""
        main_logger = self.get_logger('main')
        main_logger.info("=" * 60)
        main_logger.info("⏹️  LightBox system shutting down")
        main_logger.info(f"📅 Shutdown time: {datetime.now().isoformat()}")
        main_logger.info("=" * 60)
    
    def log_performance_metrics(self, fps, memory_mb, cpu_percent, frame_count):
        """Log performance metrics in structured format"""
        perf_logger = self.get_logger('performance')
        perf_logger.info(f"{fps},{memory_mb},{cpu_percent},{frame_count}")
    
    def get_recent_logs(self, component='main', lines=100):
        """Get recent log entries for specified component"""
        try:
            log_file = self.log_dir / f"{component}.log"
            if not log_file.exists():
                return []
            
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
                
        except Exception as e:
            error_logger = self.get_logger('errors')
            error_logger.error(f"Failed to read log file for {component}: {e}")
            return []

# Global logger instance
_lightbox_logger = None

def get_lightbox_logger():
    """Get the global LightBox logger instance"""
    global _lightbox_logger
    if _lightbox_logger is None:
        _lightbox_logger = LightBoxLogger()
    return _lightbox_logger

def setup_logging(log_dir="logs", max_size_mb=10, backup_count=5):
    """Setup LightBox logging system"""
    global _lightbox_logger
    _lightbox_logger = LightBoxLogger(log_dir, max_size_mb, backup_count)
    return _lightbox_logger

# Convenience functions
def get_logger(component='main'):
    """Get logger for specified component"""
    return get_lightbox_logger().get_logger(component)

def log_startup(version="1.0", config_summary=None):
    """Log system startup"""
    get_lightbox_logger().log_startup(version, config_summary)

def log_shutdown():
    """Log system shutdown"""
    get_lightbox_logger().log_shutdown()

def log_performance(fps, memory_mb, cpu_percent, frame_count):
    """Log performance metrics"""
    get_lightbox_logger().log_performance_metrics(fps, memory_mb, cpu_percent, frame_count)