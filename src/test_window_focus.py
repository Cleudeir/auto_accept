#!/usr/bin/env python3
"""
Test script for the enhanced window focusing functionality
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.config_model import ConfigModel
from models.window_model import WindowModel

def test_window_detection():
    print("Testing Dota 2 window detection...")
    config = ConfigModel()
    window_model = WindowModel(config)

    # Test process detection
    dota_processes = window_model.get_dota2_processes()
    print(f"Found {len(dota_processes)} Dota 2 processes:")
    for proc in dota_processes:
        print(f"  - {proc['name']} (PID: {proc['pid']}) - {proc['exe']}")
    print()

    # Test window detection
    dota_windows = window_model.get_dota2_windows()
    print(f"Found {len(dota_windows)} Dota 2 windows:")
    for window in dota_windows:
        print(f"  - Title: {window['title']}")
        print(f"    PID: {window['pid']}")
        print(f"    Process: {window['process_name']}")
        print(f"    Minimized: {window['is_minimized']}")
        print(f"    Visible: {window['is_visible']}")
        print()

    # Test enhanced focus
    if dota_windows:
        print("Testing enhanced focus (this will attempt to focus Dota 2)...")
        success = window_model.focus_dota2_window_enhanced()
        print(f"Focus attempt result: {success}")
    else:
        print("No Dota 2 windows found to focus.")

if __name__ == "__main__":
    test_window_detection()
