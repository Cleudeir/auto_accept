# Dota 2 Auto Accept

A utility that automatically detects and accepts Dota 2 match pop-ups.

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
