#!/usr/bin/env python3
"""
Test the actual application with debug output
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from controllers.main_controller import MainController
import time

def test_application():
    """Test the actual application with debug output"""
    print("🚀 Starting Dota 2 Auto Accept application test...")
    print("=" * 50)
    
    try:
        # Create the main controller
        controller = MainController()
        
        # Start detection for a few seconds to see debug output
        print("\n📱 Starting detection for 10 seconds...")
        print("=" * 50)
        
        controller.detection_controller.start_detection()
        
        # Wait for 10 seconds to capture some debug output
        time.sleep(10)
        
        print("\n🛑 Stopping detection...")
        controller.detection_controller.stop_detection()
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Application test completed!")

if __name__ == "__main__":
    test_application()
