#!/usr/bin/env python3
"""
Test enhanced window focusing functionality
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.config_model import ConfigModel
from models.window_model import WindowModel

def test_enhanced_focus():
    print("🔄 Testing Enhanced Dota 2 Window Focus...")
    
    try:
        # Create config and window model
        config = ConfigModel()
        window_model = WindowModel(config)
        
        # Test process detection
        print("📋 Checking for Dota 2 processes...")
        dota_processes = window_model.get_dota2_processes()
        print(f"Found {len(dota_processes)} Dota 2 processes:")
        for proc in dota_processes:
            print(f"  - {proc['name']} (PID: {proc['pid']})")
        
        # Test window detection
        print("\n🪟 Checking for Dota 2 windows...")
        dota_windows = window_model.get_dota2_windows()
        print(f"Found {len(dota_windows)} Dota 2 windows:")
        for window in dota_windows:
            print(f"  - Title: '{window['title']}'")
            print(f"    PID: {window['pid']}")
            print(f"    Process: {window['process_name']}")
            print(f"    Minimized: {window['is_minimized']}")
            print(f"    Visible: {window['is_visible']}")
            print()
        
        if dota_windows:
            print("🎯 Testing enhanced window focus...")
            print("This will attempt to bring Dota 2 to the foreground...")
            
            success = window_model.focus_dota2_window_enhanced()
            
            if success:
                print("✅ Enhanced window focus SUCCESS!")
                print("🎮 Dota 2 should now be in the foreground")
            else:
                print("❌ Enhanced window focus FAILED")
                print("🔍 Check the logs above for details")
        else:
            print("ℹ️  No Dota 2 windows found to focus")
            print("💡 Make sure Dota 2 is running and try again")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_focus()
