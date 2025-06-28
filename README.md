# Dota 2 Auto Accept

A utility that automatically detects and accepts Dota 2 match pop-ups, saving you from missing queue accepts while you're AFK.

## Features

- **Automatic Match Acceptance**: Detects when a Dota 2 match is found and automatically accepts it
- **Sound Alerts**: Plays audio notification when a match is found
- **Multiple Monitor Support**: Works with any monitor setup
- **Customizable Settings**: Configure alert volume, monitor selection, and audio output device
- **Screenshot Preview**: See the latest captured screenshot in the GUI
- **Debug Screenshots**: (If enabled) saves screenshots for troubleshooting
- **Minimized Operation**: Runs in the system tray for non-intrusive operation
- **Keyboard Shortcuts**: F1 (Start), F2 (Stop), F3 (Test Sound), F4 (Take Screenshot)

## Project Structure

```
auto_accept.bat                # Windows installer and launcher script
build_and_run.ps1              # PowerShell script to build and run the executable
main.spec                      # PyInstaller spec file for building the app
config.json                    # (Optional) Global config file
README.md
src/
  main.py                      # Main entry point
  requirements.txt             # Python dependencies
  config.json                  # App config (used at runtime)
  bin/                         # Images, icons, and sound resources
    AD.png
    dota.png
    dota2.mp3
    dota2_plus.jpeg
    icon.ico
    long_time.png
    print.png
    read_check.jpg
    watch-game.png
  controllers/                 # App logic controllers
    main_controller.py
    detection_controller.py
  models/                      # Data models and business logic
    config_model.py
    audio_model.py
    detection_model.py
    screenshot_model.py
  views/                       # GUI components
    main_view.py
  venv/                        # (Optional) Python virtual environment
  debug_screenshots/           # (Created at runtime if needed)
dist/
  v002-autoaccept.exe          # Built executable (after running build)
build/                         # PyInstaller build artifacts
```

## Installation

### Option 1: One-Click Setup and Run (Recommended)

1. Double-click `auto_accept.bat` (right-click and "Run as administrator" if possible)
   - Installs Python if needed
   - Installs all dependencies
   - Launches the app

### Option 2: Build Standalone Executable

1. Open PowerShell and run `build_and_run.ps1`
   - Requires Python and PyInstaller
   - Produces an `.exe` in the `dist/` folder
   - Run the `.exe` to launch the app

### Option 3: Manual Setup (Advanced)

1. Install Python 3.9+ (https://www.python.org/downloads/)
2. Open a terminal in the `src/` folder
3. Run `pip install -r requirements.txt`
4. Run `python main.py` to start the app

## Usage

- The app launches a GUI and runs minimized in the system tray
- Configure your monitor, audio device, and alert volume in the GUI
- Use the control buttons or keyboard shortcuts:
  - F1: Start Detection
  - F2: Stop Detection
  - F3: Test Sound
  - F4: Take Screenshot
- The app will automatically:
  - Monitor for Dota 2 match pop-ups
  - Play a sound when a match is found
  - Click the accept button automatically
- To close, right-click the tray icon or close the window

## Configuration

The app uses a config file (`src/config.json` or `config.json` in the root) with options:

- `alert_volume`: Volume level for match alerts (0.0 to 1.0)
- `selected_device_id`: ID of the audio output device
- `selected_monitor_capture_setting`: Monitor index for capture
- `always_on_top`: Whether the window stays on top

## Building

- To build a standalone executable, use `build_and_run.ps1` (PowerShell) or run PyInstaller manually:
  - `pyinstaller main.spec`
- All resources in `src/bin/` and config files are bundled automatically

## Dependencies

- All dependencies are listed in `src/requirements.txt` (over 80 packages, including OpenCV, PyAutoGUI, pygame, sounddevice, Pillow, scikit-image, etc.)
- The installer script (`auto_accept.bat`) will install all required packages

## Troubleshooting

- If the app isn't detecting matches:
  1. Make sure Dota 2 is running on the selected monitor
  2. Check for errors in the terminal or command prompt
  3. If debug screenshots are enabled, check `src/debug_screenshots/` (created at runtime)
  4. Ensure your Dota 2 UI is unmodified
  5. Try a different monitor or audio device
  6. Restart the app and Dota 2
- If you see missing dependencies, rerun `auto_accept.bat` or `pip install -r src/requirements.txt`

## System Requirements

- **Operating System**: Windows 10/11
- **Python**: Version 3.9 or higher (auto-installed if missing)
- **Screen Resolution**: 1080p or higher recommended
- **Storage**: ~50MB of disk space

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the need to avoid missing Dota 2 queue accepts
- Thanks to the Python community for the amazing libraries that made this possible
