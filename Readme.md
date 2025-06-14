# Dota 2 Auto Accept

A utility that automatically detects and accepts Dota 2 match pop-ups.

## Architecture

The application has been refactored to follow the MVC (Model-View-Controller) pattern for better code organization and maintainability.

### Project Structure

```
src/
├── main.py                    # Main entry point
├── models/                    # Data models and business logic
│   ├── __init__.py
│   ├── config_model.py        # Configuration management
│   ├── audio_model.py         # Audio system handling
│   ├── screenshot_model.py    # Screenshot capture functionality
│   └── detection_model.py     # Image detection and comparison
├── views/                     # User interface components
│   ├── __init__.py
│   └── main_view.py          # Main GUI window
├── controllers/               # Application logic coordinators
│   ├── __init__.py
│   ├── main_controller.py     # Main application controller
│   └── detection_controller.py # Detection logic controller
├── bin/                       # Binary resources
├── logs/                      # Application logs
└── debug_screenshots/         # Debug screenshots
```

### Components

#### Models
- **ConfigModel**: Handles loading, saving, and managing application configuration
- **AudioModel**: Manages audio system initialization and sound playback
- **ScreenshotModel**: Handles monitor detection and screenshot capture
- **DetectionModel**: Performs image comparison and match detection logic

#### Views
- **MainView**: Creates and manages the main GUI window and user interactions

#### Controllers
- **MainController**: Coordinates between all models and views, handles application lifecycle
- **DetectionController**: Manages the detection loop and threading

## Usage

### Running the Application

```bash
cd src
python main.py
```

### Legacy Entry Point

The original `accept.py` file is still available for backward compatibility, but it's recommended to use the new MVC structure via `main.py`.

## Build Instructions

This repository includes two build scripts to create an executable:

### Simple Build

1. Double-click `build_exe.bat` to create a single executable file.
2. The output will be in the `dist` folder.

### Advanced Build

`build_advanced.bat` provides more options for building the application:

1. Open Command Prompt in the project directory.
2. Run the build script with desired options:

```
build_advanced.bat [--onedir] [--debug] [--clean]
```

Options:
- `--onedir`: Create a directory containing the executable and dependent files (default is single-file)
- `--debug`: Build with debug information
- `--clean`: Clean previous build files before building

Examples:
```
build_advanced.bat                    # Build single-file executable (release mode)
build_advanced.bat --onedir           # Build directory-based executable
build_advanced.bat --debug --clean    # Build single-file executable with debug info, cleaning first
```

## Application Files

The build scripts will package the following files into the executable:

- `accept.py`: Main application script
- `dota.png`: Reference image for match detection
- `print.png`: Reference image for match detection
- `dota2.mp3`: Alert sound when match is found
- `icon.ico`: Application icon
- `config.json`: Configuration file

## Requirements

The following Python packages are required (installed automatically by the build scripts):
- python-dotenv
- pywin32
- screeninfo
- pyautogui
- opencv-python
- numpy
- pyinstaller
- pygame
- sounddevice

## Usage

After building, you can run the application by:
1. Opening the executable in the `dist` folder
2. Configure your audio settings and monitor selection
3. Click "Start Detection"
4. When a Dota 2 match is found, the application will play a sound alert

Keyboard shortcuts:
- F1: Start detection
- F2: Stop detection
- F3: Test sound
