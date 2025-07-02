#!/usr/bin/env python3
"""
Final test for the complete enhanced window focusing integration
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.config_model import ConfigModel
from models.detection_model import DetectionModel

def test_complete_integration():
    print("🚀 Testing Complete Enhanced Window Focusing Integration")
    print("=" * 60)
    
    try:
        # Initialize the components
        print("⚙️ Initializing configuration...")
        config = ConfigModel()
        print(f"   Enhanced focus enabled: {config.enhanced_window_focus}")
        print(f"   Auto focus on detection: {config.auto_focus_on_detection}")
        print(f"   Focus retry attempts: {config.focus_retry_attempts}")
        print(f"   Focus delay: {config.focus_delay_ms}ms")
        
        print("\n🔍 Initializing detection model...")
        detection_model = DetectionModel(config_model=config)
        print("   Detection model ready with enhanced window focusing")
        
        # Test the debug info
        print("\n📊 Getting Dota 2 debug information...")
        debug_info = detection_model.get_dota2_window_debug_info()
        
        if debug_info:
            print(f"   Processes found: {len(debug_info['processes'])}")
            for proc in debug_info['processes']:
                print(f"     - {proc['name']} (PID: {proc['pid']})")
            
            print(f"   Windows found: {len(debug_info['windows'])}")
            for window in debug_info['windows']:
                print(f"     - {window['title']} (PID: {window['pid']}, Minimized: {window['is_minimized']})")
        
        # Test enhanced focusing directly
        print("\n🎯 Testing enhanced window focusing...")
        success = detection_model.focus_dota2_window_enhanced()
        
        if success:
            print("✅ ENHANCED WINDOW FOCUSING WORKS PERFECTLY!")
            print("🎮 Dota 2 should now be in the foreground")
            
            # Simulate a match detection action
            print("\n🎉 Simulating match detection...")
            print("   (This would normally happen when a match is found)")
            action = detection_model.process_detection_result("dota")
            print(f"   Action taken: {action}")
            
        else:
            print("❌ Enhanced window focusing failed")
            print("🔍 Please check if Dota 2 is running")
        
        print("\n" + "=" * 60)
        print("🏁 INTEGRATION TEST COMPLETE")
        
        if success:
            print("✅ RESULT: Enhanced Dota 2 window focusing is WORKING!")
            print("🎯 Your matches will now be accepted reliably!")
        else:
            print("⚠️  RESULT: Focus test failed - check Dota 2 status")
            
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_integration()
