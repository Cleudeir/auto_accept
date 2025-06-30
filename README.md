# Auto Accept

Auto Accept is a Python-based automation tool designed to streamline repetitive tasks, likely related to game or application interactions. The project includes detection, audio, and screenshot models, as well as controllers and a simple GUI.

## Features

- Automated detection and response system
- Audio and screenshot processing
- Modular architecture (controllers, models, views)
- Configurable via `config.json`
- Easy to build and run (see below)

## Project Structure

```
app.png
build_and_run.ps1
config.json
main.spec
version.txt
build/
src/
  bin/           # Assets (images, audio)
  controllers/   # Logic controllers
  models/        # Data and processing models
  views/         # GUI components
```

## Getting Started

### Prerequisites

- Python 3.10+
- Recommended: Create a virtual environment

### Installation

1. Clone the repository or download the source code.
2. Install dependencies:

   ```powershell
   pip install -r src/requirements.txt
   ```

### Running the Application

- To run the main script:

  ```powershell
  python src/main.py
  ```

- Or use the provided PowerShell script:

  ```powershell
  ./build_and_run.ps1
  ```

### Configuration

- Edit `src/config.json` to adjust settings as needed.

## Build

- The project can be packaged using PyInstaller (see `main.spec`).

## Version

- Current version: 1.0.0

## License

Specify your license here.

## Author

Cleudeir Silva
