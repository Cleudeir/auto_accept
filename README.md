# Dota 2 Auto Accept

A cross-platform automation tool that automatically accepts Dota 2 matches by detecting the match found popup and interacting with the game window. Built with an MVC architecture for maintainability and extensibility.

## Features
- Automatic detection and acceptance of Dota 2 matches
- Screenshot and audio-based detection
- Configurable UI (classic and modern)
- Telegram notifications for match found events
- Windows and Linux support (with platform-specific requirements)
- Easy configuration via `config.json`

## Project Structure
- `src/main.py`: Main entry point
- `src/controllers/`: Controllers for detection and main logic
- `src/models/`: Models for configuration, audio, detection, screenshots, and window management
- `src/views/`: UI views (classic and modern)
- `src/requirements.txt`: Cross-platform and Windows-specific dependencies
- `config.json`: User configuration (volume, UI, Telegram, etc.)
- `build_and_run.ps1`: Script to build and run the app on Windows

## Installation
1. **Clone the repository**
2. **Install dependencies**
   - Windows: `pip install -r src/requirements_windows.txt`
   - Linux: `pip install -r src/requirements_linux.txt`
   - Or for all: `pip install -r src/requirements.txt`
3. **Configure `config.json`** as needed (Telegram, UI, etc.)

## Usage
- **Windows:**
  - Run `build_and_run.ps1` to build and launch the app as an executable
  - Or run `python src/main.py` for development
- **Linux:**
  - Run `python3 src/main.py`

## Configuration
Edit `config.json` to adjust:
- Alert volume
- UI theme and type
- Detection threshold
- Telegram notifications
- Window focus options

## License
MIT License
