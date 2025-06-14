#!/usr/bin/env python3
"""
Dota 2 Auto Accept - Main Entry Point
MVC Architecture Implementation
"""

import sys
import os

# Add the src directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.main_controller import MainController

def main():
    """Main entry point for the application"""
    try:
        # Create and run the main controller
        controller = MainController()
        # The detection will start automatically in the controller
        controller.run()
        print("Dota 2 Auto Accept is running. Press Ctrl+C to exit.")
    except KeyboardInterrupt:
        print("Application interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
