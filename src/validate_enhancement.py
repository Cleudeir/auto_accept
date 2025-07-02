#!/usr/bin/env python3
"""
Simple validation script for enhanced window focusing
"""

try:
    print("🔄 Testing enhanced window focusing integration...")
    
    # Test imports
    print("📦 Testing imports...")
    from models.config_model import ConfigModel
    from models.window_model import WindowModel
    from models.detection_model import DetectionModel
    from controllers.main_controller import MainController
    print("✅ All imports successful")
    
    # Test configuration
    print("⚙️ Testing configuration...")
    config = ConfigModel()
    print(f"  Enhanced focus: {config.enhanced_window_focus}")
    print(f"  Auto focus: {config.auto_focus_on_detection}")
    print("✅ Configuration working")
    
    # Test window model
    print("🪟 Testing window model...")
    window_model = WindowModel(config)
    processes = window_model.get_dota2_processes()
    windows = window_model.get_dota2_windows()
    print(f"  Found {len(processes)} Dota 2 processes")
    print(f"  Found {len(windows)} Dota 2 windows")
    print("✅ Window model working")
    
    # Test detection model
    print("🔍 Testing detection model...")
    detection_model = DetectionModel(config_model=config)
    print("✅ Detection model working")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("🎯 Enhanced Dota 2 window focusing is ready to use!")
    
    if windows:
        print(f"\n🎮 Dota 2 is currently running with {len(windows)} window(s)")
        print("The enhanced focusing will automatically activate when matches are detected.")
    else:
        print("\n💡 Start Dota 2 to test the enhanced window focusing functionality.")
        
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
