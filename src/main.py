#!/usr/bin/env python3
"""
Dota 2 Auto Accept - Main Entry Point
MVC Architecture Implementation
"""

import sys
import os
import logging
import traceback
from datetime import datetime

# Configure logging to a file so errors are visible even in bundled exe
if hasattr(sys, "_MEIPASS"):
    exe_dir = os.path.dirname(sys.executable)
else:
    exe_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(exe_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"auto_accept_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Use sys.__stdout__ which is always available even in windowed apps
output_stream = sys.stdout if sys.stdout is not None else sys.__stdout__

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(output_stream),
    ],
)

logger = logging.getLogger("Dota2AutoAccept")

# Write a startup marker to verify logging is working
logger.info("=" * 60)
logger.info("Logging initialized successfully")

# Add the src directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules with error handling to capture import errors
try:
    from controllers.main_controller import MainController
except Exception as e:
    logger.critical(f"Failed to import MainController: {e}", exc_info=True)
    show_error_popup("Dota 2 Auto Accept - Erro de Importação",
                     f"Falha ao importar módulo: {e}\n\n{traceback.format_exc()}")
    sys.exit(1)


def show_error_popup(title, message):
    """Show a GUI error messagebox. Safe to call even if tkinter isn't initialized."""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        pass  # If even messagebox fails, nothing more we can do


def main():
    """Main entry point for the application"""
    try:
        logger.info("Starting Dota 2 Auto Accept...")
        # Create and run the main controller
        controller = MainController()
        # The detection will start automatically in the controller
        controller.run()
        logger.info("Dota 2 Auto Accept exited normally.")
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        error_msg = f"Fatal error: {e}\n\n{traceback.format_exc()}"
        logger.critical(error_msg)
        # Also show a popup so the user sees the error
        show_error_popup("Dota 2 Auto Accept - Erro Fatal", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
