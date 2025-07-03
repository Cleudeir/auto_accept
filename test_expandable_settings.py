#!/usr/bin/env python3
"""
Test script for the expandable settings menu functionality
"""
import sys
import os
import tkinter as tk
from tkinter import ttk

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from views.main_view import MainView

def test_expandable_settings():
    """Test the expandable settings menu"""
    print("Testing expandable settings menu...")
    
    # Create the main view
    view = MainView("Test - Expandable Settings")
    
    # Create the window
    window = view.create_window()
    
    # Add a test button to toggle settings programmatically
    test_frame = tk.Frame(window, bg="#ffffff")
    test_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=5)
    
    test_btn = tk.Button(
        test_frame,
        text="Toggle Settings (Test)",
        command=view._toggle_settings,
        bg="#ff9800",
        fg="#fff",
        font=("Segoe UI", 10, "bold"),
        padx=20,
        pady=5
    )
    test_btn.pack()
    
    # Add status text to show current state
    status_label = tk.Label(
        test_frame,
        text=f"Settings Expanded: {view.settings_expanded}",
        font=("Segoe UI", 10),
        bg="#ffffff"
    )
    status_label.pack(pady=5)
    
    def update_status():
        status_label.config(text=f"Settings Expanded: {view.settings_expanded}")
        window.after(100, update_status)
    
    update_status()
    
    print("Test window created. You can:")
    print("1. Click the '▶ Settings' button to expand/collapse")
    print("2. Click the 'Toggle Settings (Test)' button to test programmatically")
    print("3. Observe the window resizing and settings panel visibility")
    print("4. Close the window when done testing")
    
    # Start the main loop
    view.mainloop()

if __name__ == "__main__":
    test_expandable_settings()
