# Dota Auto Accept Script

## Setup and Compilation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11

### Installation Steps
1. Clone the repository or download the script
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Preparing Icon and Background Image
1. Create an icon for your application (optional)
   - Use tools like Photoshop, GIMP, or online icon converters
   - Recommended size: 256x256 pixels
   - Save as `.ico` format

2. Prepare the reference image (dota.png)
   - Capture a clear screenshot of the Dota 2 match accept button
   - Ensure high contrast and visibility

### Compiling to Executable
1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Compile the script:
   ```
   pyinstaller --onefile --windowed --icon=your_icon.ico dota_auto_accept.py
   ```

### Compilation Options
- `--onefile`: Creates a single executable
- `--windowed`: Prevents console window from appearing
- `--icon=your_icon.ico`: Adds a custom icon to the executable

### Troubleshooting
- Ensure all dependencies are installed
- Verify the reference image path is correct
- Check screen resolution compatibility#   a u t o _ a c c e p t  
 #   a u t o _ a c c e p t  
 