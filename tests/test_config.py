#!/usr/bin/env python3
"""Tests for config.py module"""

import pytest
import sys
import os
from pathlib import Path

# Add LightBox directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "LightBox"))

from config import Config

def test_config_initialization():
    """Test that Config class initializes properly"""
    config = Config()
    assert config.matrix_width == 10
    assert config.matrix_height == 10
    assert isinstance(config.brightness, float)
    assert 0.0 <= config.brightness <= 1.0

def test_config_xy_to_index():
    """Test matrix coordinate conversion"""
    config = Config()
    # Test corner coordinates
    assert config.xy_to_index(0, 0) == 0
    assert config.xy_to_index(9, 0) == 9
    
def test_config_mark_updated():
    """Test configuration change detection"""
    config = Config()
    initial_counter = config._update_counter
    config.mark_updated()
    assert config._update_counter > initial_counter

def test_config_has_updates():
    """Test update detection mechanism"""
    config = Config()
    import time
    timestamp = time.time()
    counter = config._update_counter
    
    # Should have no updates initially
    assert not config.has_updates(timestamp, counter)
    
    # Should detect updates after marking
    config.mark_updated()
    assert config.has_updates(timestamp, counter)