#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Title and Welcome
echo "==========================================="
echo " Dota Auto Accept - Compilation Script (Linux/macOS)"
echo "==========================================="
echo

# remove all files in dist and build folders
echo "Cleaning previous builds..."
rm -rf dist build

# Check Python installation (prefer python3)
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "Error: Python not found. Please install Python 3."
    exit 1
fi
echo "Using Python command: $PYTHON_CMD"

# Check pip
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo "Error: pip not found for $PYTHON_CMD. Please ensure pip is installed."
    exit 1
fi

# Check PyInstaller
echo "Checking for PyInstaller..."
if ! $PYTHON_CMD -m pip list | grep -i "pyinstaller" &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    $PYTHON_CMD -m pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install PyInstaller."
        exit 1
    fi
else
    echo "PyInstaller found."
fi

# Set variables
SCRIPT_NAME="dota_auto_accept.py"
ICON_NAME="icon.icns" # macOS uses .icns, Linux often uses .png or none for windowed apps
REFERENCE_IMAGE="dota.png"
ENV_FILE=".env"
APP_NAME="DotaAutoAccept"

# Validate script exists
if [ ! -f "$SCRIPT_NAME" ]; then
    echo "Error: $SCRIPT_NAME not found in current directory."
    exit 1
fi

# Validate reference image exists
if [ ! -f "$REFERENCE_IMAGE" ]; then
    echo "Error: Reference image $REFERENCE_IMAGE not found in current directory."
    exit 1
fi

# Validate .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found in current directory."
    exit 1
fi

# Handle Icon (macOS specific .icns, Linux often doesn't use --icon this way)
ICON_PARAM=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if [ -f "$ICON_NAME" ]; then
        echo "Using icon file: $ICON_NAME"
        ICON_PARAM="--icon="$ICON_NAME""
    else
        echo "Warning: No macOS icon file ($ICON_NAME) found. Compiling without custom icon."
        # Consider adding a default icon or handling Linux icons if needed
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
     # Linux - PyInstaller --icon usually expects .ico or .icns, might not work reliably with window managers for .png
     echo "Note: Custom icon setting might vary on Linux distributions."
     if [ -f "icon.png" ]; then
         echo "Found icon.png, but PyInstaller icon support on Linux can be inconsistent."
         # ICON_PARAM="--icon="icon.png"" # Uncomment if you want to try using a png icon
     elif [ -f "icon.ico" ]; then
         echo "Found icon.ico. Attempting to use it."
         ICON_PARAM="--icon="icon.ico""
     else
         echo "No specific Linux icon found (icon.png or icon.ico)."
     fi
fi


# Create dist and build directories
mkdir -p dist build

# Compile the script with additional data files
echo "Compiling $SCRIPT_NAME..."

# Note: On macOS, creating a .app bundle (--windowed without --onefile) is often preferred for GUI apps.
# --onefile creates a single executable, which might be simpler but less standard for macOS GUI.
# Adding ':' for Linux/macOS path separator in --add-data
PYINSTALLER_CMD="$PYTHON_CMD -m PyInstaller --onefile --windowed --name "$APP_NAME" \
    --add-data "$REFERENCE_IMAGE:." \
    --add-data "$ENV_FILE:." \
    --clean \
    --distpath "dist" \
    --workpath "build" \
    $ICON_PARAM \
    "$SCRIPT_NAME""

echo "Running PyInstaller command:"
echo "$PYINSTALLER_CMD"
eval $PYINSTALLER_CMD # Use eval to handle the quotes in ICON_PARAM correctly

# Check compilation result
if [ $? -eq 0 ]; then
    echo "Compilation successful!"
    echo "Executable located in: dist/$APP_NAME"
    # Attempt to open the directory, might not work on all systems/environments
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open dist
    elif command -v xdg-open &> /dev/null; then
        xdg-open dist
    else
        echo "Please navigate to the 'dist' directory to find the executable."
    fi
else
    echo "Compilation failed."
    exit 1
fi

echo "Script finished." 