#!/usr/bin/env python3
"""
Test script for the modern UI rebranding with CustomTkinter
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_modern_ui():
    """Test the modern rebranded UI"""
    print("🎨 Testing Modern UI Rebranding...")
    
    from models.config_model import ConfigModel
    from views.modern_main_view import ModernMainView
    
    # Create config with modern UI enabled
    config = ConfigModel("modern_test_config.json")
    config.use_modern_ui = True
    config.ui_theme = "dark"
    
    print(f"Modern UI enabled: {config.use_modern_ui}")
    print(f"Theme: {config.ui_theme}")
    
    # Create modern view
    view = ModernMainView("🎮 Dota 2 Auto Accept - Modern UI", config_model=config)
    
    # Create window
    window = view.create_window()
    
    print("\n🚀 Modern UI Features:")
    print("   ✨ Dark/Light theme toggle (🌙/☀️ button)")
    print("   🎯 Modern progress bars and sliders")
    print("   📱 Card-based layout design")
    print("   🔄 Smooth animations and transitions")
    print("   ⚙️ Improved settings panel")
    print("   🎨 Modern color scheme and typography")
    print("   📐 Responsive grid layout")
    print("   💫 Rounded corners and shadows")
    
    print("\n🎮 How to test:")
    print("   1. Click 🌙 to toggle light/dark theme")
    print("   2. Click ⚙️ to show/hide settings panel")
    print("   3. Test all buttons and sliders")
    print("   4. Resize window to see responsive behavior")
    print("   5. Close when done testing")
    
    # Start the modern UI
    view.mainloop()
    
    # Clean up test config
    if os.path.exists("modern_test_config.json"):
        os.remove("modern_test_config.json")
    
    print("✅ Modern UI test completed!")

def test_ui_comparison():
    """Show comparison between old and new UI"""
    print("\n📊 UI Comparison:")
    print("┌─────────────────┬─────────────────────┬──────────────────────┐")
    print("│ Feature         │ Original UI         │ Modern UI            │")
    print("├─────────────────┼─────────────────────┼──────────────────────┤")
    print("│ Framework       │ tkinter             │ CustomTkinter        │")
    print("│ Theme Support   │ System only         │ Dark/Light/System    │")
    print("│ Visual Style    │ Classic widgets     │ Modern flat design   │")
    print("│ Color Scheme    │ Basic system colors │ Modern blue palette  │")
    print("│ Corners         │ Sharp rectangles    │ Rounded corners      │")
    print("│ Layout          │ Fixed positioning   │ Responsive grid      │")
    print("│ Progress Bars   │ Basic system bar    │ Modern styled bar    │")
    print("│ Buttons         │ 3D system buttons   │ Flat modern buttons  │")
    print("│ Typography      │ System font         │ CTkFont with weights │")
    print("│ Icons           │ Text only           │ Emoji + text         │")
    print("│ Responsiveness  │ Fixed size          │ Resizable layout     │")
    print("│ Animation       │ None                │ Smooth transitions   │")
    print("└─────────────────┴─────────────────────┴──────────────────────┘")

if __name__ == "__main__":
    print("🎨 MODERN UI REBRANDING TEST")
    print("=" * 50)
    
    test_ui_comparison()
    
    try:
        test_modern_ui()
        
        print("\n🎉 Modern UI Rebranding Complete!")
        print("\n📋 New Features Added:")
        print("   ✅ CustomTkinter modern framework")
        print("   ✅ Dark/Light theme toggle")
        print("   ✅ Modern card-based layout")
        print("   ✅ Responsive grid system")
        print("   ✅ Improved visual hierarchy")
        print("   ✅ Modern color palette")
        print("   ✅ Enhanced typography")
        print("   ✅ Smooth animations")
        print("   ✅ Mobile-inspired design")
        print("   ✅ Configuration persistence")
        
    except Exception as e:
        print(f"❌ Error testing modern UI: {e}")
        import traceback
        traceback.print_exc()
