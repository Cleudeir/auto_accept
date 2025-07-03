#!/usr/bin/env python3
"""
Test script to validate the settings panel expansion improvements.
This script creates a simple test window to demonstrate the smooth toggle functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from src.models.config_model import ConfigModel
from src.views.main_view import MainView
from src.views.modern_main_view import ModernMainView

def test_traditional_ui():
    """Test the traditional UI settings expansion"""
    print("Testing Traditional UI...")
    config = ConfigModel()
    view = MainView(config_model=config)
    
    window = view.create_window()
    
    # Add test button to toggle settings
    test_frame = tk.Frame(window, bg="#ffffff")
    test_frame.pack(side="bottom", fill="x", pady=10)
    
    toggle_btn = tk.Button(
        test_frame,
        text="Toggle Settings (Test)",
        command=view._toggle_settings,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        padx=20,
        pady=10
    )
    toggle_btn.pack()
    
    status_label = tk.Label(
        test_frame,
        text="Press F5 or click 'Toggle Settings (Test)' to test smooth expansion",
        bg="#ffffff",
        font=("Arial", 10),
        fg="#666"
    )
    status_label.pack(pady=5)
    
    window.mainloop()

def test_modern_ui():
    """Test the modern UI settings expansion"""
    print("Testing Modern UI...")
    try:
        import customtkinter as ctk
        config = ConfigModel()
        view = ModernMainView(config_model=config)
        
        window = view.create_window()
        
        # Add test button to toggle settings
        test_btn = ctk.CTkButton(
            view.main_container,
            text="Toggle Settings (Test)",
            command=view._toggle_settings,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        test_btn.grid(row=3, column=0, pady=20)
        
        window.mainloop()
    except ImportError:
        print("CustomTkinter not available. Please install it to test modern UI.")
        print("Run: pip install customtkinter")

def main():
    """Main test function"""
    print("Settings Panel Expansion Test")
    print("=" * 40)
    print("1. Traditional UI Test")
    print("2. Modern UI Test")
    print("3. Exit")
    
    choice = input("\nSelect test (1-3): ").strip()
    
    if choice == "1":
        test_traditional_ui()
    elif choice == "2":
        test_modern_ui()
    elif choice == "3":
        print("Exiting...")
        return
    else:
        print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
