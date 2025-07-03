# Enhanced Dota 2 Window Focusing Strategy

This update implements a comprehensive window management system for the Dota 2 Auto Accept application, ensuring reliable window focusing when image detections occur.

## New Features

### 1. Enhanced Window Focusing

- **Multiple Strategy Approach**: Uses Windows API, pygetwindow, and process-based methods
- **Retry Logic**: Configurable retry attempts with delays between attempts
- **Smart Window Selection**: Prioritizes non-minimized windows and active Dota 2 instances

### 2. Configuration Options

New configuration parameters in `config.json`:

- `enhanced_window_focus`: Enable/disable the enhanced focusing system (default: true)
- `auto_focus_on_detection`: Automatically focus Dota 2 when any detection occurs (default: true)
- `focus_retry_attempts`: Number of retry attempts for window focusing (default: 3)
- `focus_delay_ms`: Delay between focus operations in milliseconds (default: 100)

### 3. Manual Focus Testing

- **New Button**: "🎯 Focus Dota 2" button in the UI for manual testing
- **Keyboard Shortcut**: Press F5 to manually trigger Dota 2 window focusing
- **Debugging Information**: Detailed logging of focus attempts and window states

## How It Works

### Detection Flow

1. **Image Detection**: When a Dota 2 UI element is detected (match found, accept dialog, etc.)
2. **Window Focus**: Automatically attempts to focus the Dota 2 window using multiple strategies
3. **Action Execution**: Sends the appropriate key press (Enter for accept, ESC for dismissal)
4. **Verification**: Logs success/failure of each step

### Window Focusing Strategies

#### Strategy 1: Windows API Method

- Enumerates all visible windows to find Dota 2 instances
- Uses advanced Windows API calls for forced window activation
- Handles minimized windows by restoring them first
- Verifies focus by checking the foreground window

#### Strategy 2: PyGetWindow Fallback

- Uses the original pygetwindow library method
- Simpler but less reliable than Windows API approach
- Provides compatibility with the original implementation

#### Strategy 3: Process-Based Approach

- Finds Dota 2 processes and their associated windows
- Useful when window titles are inconsistent
- Last resort method for difficult focus scenarios

### Enhanced API Methods

#### WindowModel Class

- `focus_dota2_window_enhanced()`: Main enhanced focusing method
- `get_dota2_processes()`: Find all Dota 2 related processes
- `get_dota2_windows()`: Find all Dota 2 windows with detailed info
- `force_focus_window(hwnd)`: Low-level Windows API window focusing
- `list_all_dota2_related_windows()`: Debugging method for window analysis

#### DetectionModel Updates

- Enhanced `process_detection_result()` with configurable auto-focus
- Improved error handling and logging
- Configuration-aware window focusing behavior

## Usage Examples

### Automatic Mode (Default)

The system automatically focuses Dota 2 when any detection occurs:

```python
# This happens automatically when a match is found
# 1. Image detection triggers
# 2. Dota 2 window is focused
# 3. Enter key is pressed to accept match
```

### Manual Testing

Use the new UI button or keyboard shortcut:

- Click "🎯 Focus Dota 2" button
- Press F5 key
- Check console/logs for detailed focus attempt results

### Configuration Customization

Edit `src/config.json`:

```json
{
  "enhanced_window_focus": true,
  "auto_focus_on_detection": true,
  "focus_retry_attempts": 5,
  "focus_delay_ms": 150
}
```

## Troubleshooting

### Common Issues

1. **Focus Fails**: Check if Dota 2 is running and visible
2. **Multiple Dota Instances**: The system prioritizes non-minimized windows
3. **Slow Focus**: Increase `focus_delay_ms` for better compatibility
4. **Permission Issues**: Run the application as administrator if needed

### Debug Information

Enable detailed logging to see:

- Which Dota 2 processes and windows were found
- Which focusing strategy succeeded or failed
- Timing information for each focus attempt
- Window state verification results

### Logging Output Example

```
INFO: Attempting to focus Dota 2 window: Dota 2 (PID: 12345)
INFO: Successfully focused window 123456
INFO: Match detected with highest match: dota
INFO: Pressing Enter key
```

## Technical Details

### Windows API Usage

The enhanced system uses several Windows API functions:

- `EnumWindows`: Find all windows
- `GetWindowText`: Get window titles
- `SetForegroundWindow`: Set active window
- `BringWindowToTop`: Bring window to front
- `ShowWindow`: Control window state
- `AttachThreadInput`: Handle input focus

### Process Management

Uses `psutil` library for:

- Finding Dota 2 processes
- Getting process information
- Handling process access permissions

### Error Handling

Comprehensive error handling for:

- Missing Dota 2 processes/windows
- Windows API access denied errors
- Focus verification failures
- Configuration loading issues

## Performance Impact

### Resource Usage

- Minimal additional CPU usage
- Small memory footprint increase
- Network: No impact
- Disk: Additional logging only

### Timing

- Focus attempts: 100-500ms per attempt
- Total focus time: Usually < 1 second
- Detection delay: No significant impact
- Retry overhead: Configurable

## Compatibility

### Operating System

- Windows 10 and later (primary support)
- Windows 8.1 (limited testing)
- Requires Windows API access

### Dota 2 Versions

- Compatible with all current Dota 2 versions
- Works with Dota 2 in windowed, borderless, and fullscreen modes
- Handles Dota 2 running on multiple monitors

### Dependencies

- All required packages are already in requirements.txt
- No additional installation needed
- Uses existing pygame, pywin32, and psutil libraries
