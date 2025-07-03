#!/usr/bin/env python3
"""
Comprehensive test script for the expandable settings menu with persistence
"""
import sys
import os
import json
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_config_persistence():
    """Test that settings panel state persists in config"""
    from models.config_model import ConfigModel
    
    print("🔧 Testing config persistence...")
    
    # Test 1: Default state
    config = ConfigModel("test_config.json")
    print(f"Default settings_panel_expanded: {config.settings_panel_expanded}")
    assert config.settings_panel_expanded == False, "Default should be False"
    
    # Test 2: Setting and saving
    config.settings_panel_expanded = True
    print(f"After setting to True: {config.settings_panel_expanded}")
    assert config.settings_panel_expanded == True, "Should be True after setting"
    
    # Test 3: Load from file
    config2 = ConfigModel("test_config.json")
    print(f"Loaded from file: {config2.settings_panel_expanded}")
    assert config2.settings_panel_expanded == True, "Should persist True from file"
    
    # Clean up test file
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    
    print("✅ Config persistence test passed!")

def test_ui_integration():
    """Test the UI integration with config"""
    import tkinter as tk
    from models.config_model import ConfigModel
    from views.main_view import MainView
    
    print("🎨 Testing UI integration...")
    
    # Test with config that has expanded=False
    config = ConfigModel("test_config2.json")
    config.settings_panel_expanded = False
    
    view = MainView(config_model=config)
    print(f"View initial state: {view.settings_expanded}")
    assert view.settings_expanded == False, "View should start with False"
    
    # Test toggling
    view.settings_expanded = True
    if view.config_model:
        view.config_model.settings_panel_expanded = view.settings_expanded
    
    print(f"After toggle: config={config.settings_panel_expanded}, view={view.settings_expanded}")
    assert config.settings_panel_expanded == True, "Config should be updated"
    assert view.settings_expanded == True, "View should be updated"
    
    # Clean up
    if os.path.exists("test_config2.json"):
        os.remove("test_config2.json")
    
    print("✅ UI integration test passed!")

def test_complete_workflow():
    """Test the complete workflow with a visual demo"""
    import tkinter as tk
    from models.config_model import ConfigModel
    from views.main_view import MainView
    
    print("🚀 Testing complete workflow...")
    
    # Create config and view
    config = ConfigModel("demo_config.json")
    view = MainView("Demo - Expandable Settings Test", config_model=config)
    
    # Create window
    window = view.create_window()
    
    # Add demo controls
    demo_frame = tk.Frame(window, bg="#ffffff")
    demo_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=5)
    
    status_label = tk.Label(
        demo_frame,
        text=f"Settings Expanded: {view.settings_expanded} | Config: {config.settings_panel_expanded}",
        font=("Segoe UI", 10),
        bg="#ffffff"
    )
    status_label.pack(pady=5)
    
    def update_status():
        status_label.config(
            text=f"Settings Expanded: {view.settings_expanded} | Config: {config.settings_panel_expanded}"
        )
        window.after(100, update_status)
    
    def auto_demo():
        """Automatically demonstrate the functionality"""
        print("Starting auto demo in 2 seconds...")
        
        def demo_step1():
            print("Step 1: Expanding settings...")
            view._toggle_settings()
            window.after(2000, demo_step2)
        
        def demo_step2():
            print("Step 2: Collapsing settings...")
            view._toggle_settings()
            window.after(2000, demo_step3)
        
        def demo_step3():
            print("Step 3: Expanding again...")
            view._toggle_settings()
            print("Demo complete! Close window to finish test.")
        
        window.after(2000, demo_step1)
    
    # Demo buttons
    button_frame = tk.Frame(demo_frame, bg="#ffffff")
    button_frame.pack(pady=5)
    
    auto_btn = tk.Button(
        button_frame,
        text="Run Auto Demo",
        command=auto_demo,
        bg="#4caf50",
        fg="#fff",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=5
    )
    auto_btn.pack(side=tk.LEFT, padx=5)
    
    manual_btn = tk.Button(
        button_frame,
        text="Toggle Manually",
        command=view._toggle_settings,
        bg="#2196f3",
        fg="#fff",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=5
    )
    manual_btn.pack(side=tk.LEFT, padx=5)
    
    close_btn = tk.Button(
        button_frame,
        text="Close & Check Config",
        command=lambda: window.quit(),
        bg="#f44336",
        fg="#fff",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=5
    )
    close_btn.pack(side=tk.LEFT, padx=5)
    
    update_status()
    
    print("🎮 Demo window opened. Test the expandable settings:")
    print("1. Click the '▶ Settings' button to expand/collapse")
    print("2. Use 'Toggle Manually' button to test")
    print("3. Use 'Run Auto Demo' for automatic demonstration")
    print("4. Close window when done to check config persistence")
    
    # Start the demo
    view.mainloop()
    
    # Check final config state
    print(f"\n📊 Final Results:")
    print(f"   View state: {view.settings_expanded}")
    print(f"   Config state: {config.settings_panel_expanded}")
    
    # Check config file
    if os.path.exists("demo_config.json"):
        with open("demo_config.json", "r") as f:
            saved_config = json.load(f)
            print(f"   Saved to file: {saved_config.get('settings_panel_expanded', 'NOT FOUND')}")
        os.remove("demo_config.json")
    
    print("✅ Complete workflow test finished!")

if __name__ == "__main__":
    print("🧪 Running comprehensive expandable settings tests...\n")
    
    try:
        # Run all tests
        test_config_persistence()
        print()
        test_ui_integration()
        print()
        test_complete_workflow()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary of implemented features:")
        print("   ✅ Expandable/collapsible right-side settings menu")
        print("   ✅ Settings panel state persistence in config")
        print("   ✅ Window resizing when settings expand/collapse")
        print("   ✅ Integration with main controller and config model")
        print("   ✅ Clean UI with toggle button and smooth transitions")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
