# Dota 2 Auto Accept

A utility that automatically detects and accepts Dota 2 match pop-ups, saving you from missing queue accepts while you're AFK.

## Features

- **Automatic Match Acceptance**: Detects when a Dota 2 match is found and automatically accepts it
- **Sound Alerts**: Plays audio notification when a match is found
- **Multiple Monitor Support**: Works with any monitor setup
- **Customizable Settings**: Configure volume, monitor selection, and more
- **Debug Screenshots**: Automatically saves screenshots for troubleshooting
- **Minimized Operation**: Runs in the system tray for non-intrusive operation

## Installation

### Option 1: Download and Run the Executable

1. Download the latest release from the [Releases](https://github.com/yourusername/dota2-auto-accept/releases) section (if available)
2. Extract the ZIP file to any location on your computer
3. Run `start.bat` to start the application

### Option 2: Install from Source

1. Clone the repository or download the source code
2. Right-click on `install.bat` and select "Run as administrator"
   - This script will:
     - Check if Python is installed (and install Python 3.11+ if not)
     - Install all required Python packages
     - Create a `start.bat` file
     - Create a desktop shortcut (if applicable)
3. After installation completes, you can start the application by:
   - Running `start.bat` from the installation folder
   - Or double-clicking any created desktop shortcut

> **Note**: If the installation encounters issues, you may need to manually install Python 3.9+ from [python.org](https://www.python.org/downloads/) and run `pip install -r src/requirements.txt` in a command prompt.

## Usage

1. Launch the application by running `start.bat` or any created desktop shortcut
2. The application runs minimized in the system tray by default
   - You can access the main window by clicking on the tray icon
3. Configure settings as needed:
   - Select your monitor (if you have multiple monitors)
   - Adjust alert volume using the slider
   - Toggle "Always on Top" setting to keep the window visible
4. The application will automatically:
   - Monitor for Dota 2 match pop-ups
   - Play a sound when a match is found
   - Click the accept button automatically
5. Keep the application running while you're queuing for matches
6. To close the application, right-click on the tray icon and select "Exit"

## Configuration

The application uses a configuration file (`config.json`) to store your preferences:

- `alert_volume`: Volume level for match alerts (0.0 to 1.0)
- `selected_device_id`: ID of the monitor device to use for capturing
- `selected_monitor_capture_setting`: Monitor capture method
- `always_on_top`: Whether the application window stays on top of other windows

### Debug Screenshots

The application automatically saves screenshots when it's trying to detect match accept buttons:

- Screenshots are saved in the `src/debug_screenshots/` folder
- Each screenshot is named with a timestamp: `dota2_monitor_capture_YYYYMMDD-HHMMSS.png`
- These screenshots are useful for troubleshooting if the application isn't correctly detecting match popups
- The most recent screenshots can help identify why detection might be failing

## Project Structure

The application follows the MVC (Model-View-Controller) architecture:

```
src/
├── main.py                    # Main entry point
├── models/                    # Data models and business logic
│   ├── config_model.py        # Configuration management
│   ├── audio_model.py         # Audio system handling
│   ├── screenshot_model.py    # Screenshot capture functionality
│   └── detection_model.py     # Image detection and comparison
├── views/                     # User interface components
│   └── main_view.py           # Main GUI window
├── controllers/               # Application logic coordinators
│   ├── main_controller.py     # Main application controller
│   └── detection_controller.py # Detection logic controller
├── bin/                       # Binary resources (images, sounds, icons)
│   ├── dota.png               # Reference image for match detection
│   ├── dota2-plus.jpeg        # Additional detection reference
│   ├── dota2.mp3              # Alert sound when match is found
│   ├── icon.ico               # Application icon
│   ├── long_time.png          # Long queue time detection image
│   ├── print.png              # Additional detection reference
│   └── read-check.jpg         # Ready check detection image
├── logs/                      # Application logs
│   └── dota2_auto_accept.log  # Main log file
└── src/                       # Source directory (development)
    └── debug_screenshots/     # Debug screenshots
        └── dota2_monitor_capture_*.png  # Timestamped screenshots
```

## Troubleshooting

If the application isn't detecting matches correctly:

1. Make sure Dota 2 is running in the selected monitor
2. Check the logs:
   - Main logs: `logs/dota2_auto_accept.log`
   - Look for errors or "Match found" messages
3. Check debug screenshots:
   - Screenshots are saved in `src/debug_screenshots/` folder
   - Files are named with timestamp: `dota2_monitor_capture_YYYYMMDD-HHMMSS.png`
   - Compare these with the expected Dota 2 accept button appearance
4. Verify that your Dota 2 UI hasn't been modified by mods or updates
5. Try selecting a different monitor if you have multiple screens
6. Restart the application and Dota 2
7. If problems persist, try reinstalling or checking for updated versions

## System Requirements

- **Operating System**: Windows 10/11
- **Python**: Version 3.9 or higher (automatically installed by the installer)
- **Required Libraries**: (automatically installed by the installer)
  - python-dotenv
  - pywin32
  - screeninfo
  - PyAutoGUI
  - OpenCV
  - NumPy
  - PyInstaller
  - setuptools
  - wheel
  - requests
  - pygame
  - sounddevice
  - Pillow
  - MSS
  - scikit-image
  - PyGetWindow
- **Screen Resolution**: 1080p or higher recommended
- **Storage**: ~50MB of disk space

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Dota 2 Auto Accept project was inspired by the need to avoid missing queue accepts
- Thanks to the Python community for the amazing libraries that made this possible
