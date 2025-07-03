# New Features Documentation

## Auto-Detect Dota 2 Monitor

### Overview

This feature automatically detects which monitor is currently displaying Dota 2 and sets the capture monitor accordingly.

### Usage

1. **Automatic Detection at Startup**: Enable `auto_detect_dota_monitor` in config.json to automatically detect the monitor when the application starts.
2. **Manual Detection**: Click the "🔍 Auto-detect Dota Monitor" button in the Monitor Settings section to manually trigger detection.

### Configuration

Add to `config.json`:

```json
{
  "auto_detect_dota_monitor": true
}
```

### How it Works

- Searches for visible windows containing "Dota 2" or "Dota2" in the title
- Determines which monitor contains the center of the Dota 2 window
- Automatically updates the monitor capture setting

## Detection Threshold Saving

### Overview

The detection threshold (sensitivity) is now saved to the configuration file and persists between application restarts.

### Configuration

Add to `config.json`:

```json
{
  "detection_threshold": 0.7
}
```

### Usage

- Adjust the "Detection Threshold" slider in the UI
- The value is automatically saved to config.json
- The threshold is loaded when the application starts

### Threshold Ranges

- **0.0 - 0.6**: High sensitivity (more false positives, catches more matches)
- **0.7 - 0.8**: Balanced (recommended for most users)
- **0.9 - 1.0**: Low sensitivity (fewer false positives, may miss some matches)

## Improved Monitor Screenshot Functionality

### Overview

Enhanced screenshot functionality that properly saves screenshots with timestamps and better error handling.

### Features

- Screenshots are saved to a `screenshots/` directory
- Filenames include monitor number and timestamp
- Better error messages and user feedback
- Creates directory automatically if it doesn't exist

### File Format

Screenshots are saved as: `monitor_{number}_screenshot_{timestamp}.png`

Example: `monitor_2_screenshot_20250703_143022.png`

## Configuration File Schema

### Complete Updated config.json

```json
{
  "alert_volume": 0.22,
  "selected_device_id": 6,
  "selected_monitor_capture_setting": 2,
  "always_on_top": true,
  "enhanced_window_focus": true,
  "auto_focus_on_detection": true,
  "focus_retry_attempts": 3,
  "focus_delay_ms": 150,
  "ui_theme": "dark",
  "use_modern_ui": true,
  "detection_threshold": 0.7,
  "auto_detect_dota_monitor": false
}
```

### New Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `detection_threshold` | float | 0.7 | Image detection sensitivity (0.0-1.0) |
| `auto_detect_dota_monitor` | boolean | false | Auto-detect Dota 2 monitor at startup |

## Usage Examples

### Enable Auto-Detection

1. Set `"auto_detect_dota_monitor": true` in config.json
2. Start Dota 2
3. Launch the auto-accept application
4. The correct monitor will be automatically selected

### Manual Monitor Detection

1. Launch Dota 2
2. Open the auto-accept application
3. Click "🔍 Auto-detect Dota Monitor" button
4. The monitor will be automatically detected and selected

### Adjust Detection Sensitivity

1. Move the "Detection Threshold" slider in the UI
2. The setting is automatically saved
3. Test with screenshots to find optimal sensitivity

## Technical Implementation

### Files Modified

- `src/config.json`: Added new configuration options
- `src/models/config_model.py`: Added property accessors for new options
- `src/models/screenshot_model.py`: Added auto-detection method
- `src/models/detection_model.py`: Integrated config-based threshold
- `src/controllers/main_controller.py`: Added callback handlers and initialization
- `src/views/modern_main_view.py`: Added auto-detect button and UI methods

### Dependencies

- Existing dependencies (no new requirements added)
- Uses `pygetwindow` for window detection (already in requirements)

## Troubleshooting

### Auto-Detection Not Working

- Ensure Dota 2 is running and visible
- Check that the window title contains "Dota 2" or "Dota2"
- Verify the window is not minimized

### Screenshot Issues

- Check that the selected monitor index is valid
- Ensure write permissions in the application directory
- Monitor numbering starts from 1

### Threshold Not Saving

- Verify config.json is writable
- Check for JSON syntax errors in config.json
- Ensure the application has file write permissions
