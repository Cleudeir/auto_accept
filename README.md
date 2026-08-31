# Dota 2 Auto Accept

<div align="center">

A cross-platform automation tool that automatically accepts Dota 2 matches by detecting the match found popup and interacting with the game window.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

</div>

---

## Versions

| Version | Changes |
|---------|---------|
| **3.0.0** | Compact 640x640 UI, remove periodic screenshots, clean logs |
| **2.0.0** | Auto-launch Dota 2, enhanced window focus, auto-close after game starts, Telegram notifications |
| **1.0.0** | Initial release — auto accept via SSIM detection, audio alerts, multi-monitor support |

---

## Features

- **Auto Accept Matches** — Detects the match found popup via image recognition and automatically accepts it
- **Screenshot Detection** — Uses SSIM (Structural Similarity Index) to compare reference images against screen captures
- **Audio Alerts** — Plays an alert sound when a match is found
- **Telegram Notifications** — Sends real-time notifications (and optional screenshots) to your Telegram
- **Auto Launch** — Automatically starts Discord and Dota 2 if they aren't running
- **Multi-Monitor Support** — Auto-detects which monitor Dota 2 is running on
- **Window Focus** — Automatically focuses the Dota 2 window and presses the accept button
- **Modern UI** — Built with CustomTkinter (dark/light theme support)
- **Configurable Sensitivity** — Adjustable detection threshold to fine-tune accuracy
- **PyInstaller Build** — Packages into a standalone `.exe` for Windows

---

## Project Structure

```
auto_accept/
├── config.json                    # User configuration (volume, UI, Telegram, etc.)
├── version.txt                    # Current version (auto-incremented on build)
├── auto_accept.spec               # PyInstaller spec for building the .exe
├── build_and_run.ps1              # PowerShell script to build & launch on Windows
├── src/
│   ├── main.py                    # Entry point — logging setup, error handling
│   ├── utils.py                   # Resource path resolution (dev + PyInstaller)
│   ├── requirements.txt           # All dependencies (cross-platform + Windows)
│   ├── requirements_linux.txt     # (merged into requirements.txt)
│   ├── requirements_windows.txt   # (merged into requirements.txt)
│   ├── bin/                       # Static assets
│   │   ├── icon.ico               # Application icon
│   │   ├── dota.png               # Reference image — Dota 2 accept button
│   │   ├── dota2_plus.jpeg        # Reference image — Dota 2 Plus accept button
│   │   ├── AD.png                 # Reference image — AD detection
│   │   ├── read_check.jpg         # Reference image — read check
│   │   ├── dota_plus.png          # Reference image — Dota Plus
│   │   └── 10min.png              # Reference image — 10-minute cooldown
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── main_controller.py         # Orchestrator — ties models, views, detection, and Telegram
│   │   ├── detection_controller.py    # Detection loop running in a background thread
│   │   └── enhanced_detection_controller.py  # Enhanced detection with debug output
│   ├── models/
│   │   ├── __init__.py
│   │   ├── config_model.py        # Load/save config.json, typed properties with validation
│   │   ├── detection_model.py     # Image detection logic (SSIM, OCR, center-crop matching)
│   │   ├── screenshot_model.py    # Multi-monitor screenshot capture via `mss`
│   │   ├── audio_model.py         # Audio output device listing and sound playback via `pygame`
│   │   └── window_model.py        # Window focus, Dota 2 process detection (Win32 API)
│   └── views/
│       ├── __init__.py
│       ├── main_view.py           # Classic tkinter UI
│       └── modern_main_view.py    # Modern CustomTkinter UI (default)
└── build/                         # PyInstaller build artifacts
```

---

## Architecture (MVC)

The application follows the **Model-View-Controller** pattern:

| Layer | Responsibility |
|-------|---------------|
| **Models** | Data & logic — config, detection (SSIM), screenshots, audio, window management |
| **Views** | UI — Classic (`tkinter`) or Modern (`customtkinter`) interface |
| **Controllers** | Orchestration — `MainController` coordinates everything; `DetectionController` runs the capture/detect loop in a background thread |

---

## Installation

### Prerequisites

- **Python 3.10+**
- **pip** (included with Python)
- **Git** (to clone the repo)
- **Dota 2** installed via Steam

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/auto_accept.git
cd auto_accept

# 2. (Recommended) Create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r src/requirements.txt

# 4. Configure
# Edit config.json with your preferences (see Configuration section below)
```

### Platform-Specific Dependencies

The unified `src/requirements.txt` includes everything. Windows-only packages (`pycaw`, `PyGetWindow`, `pywin32`) are automatically skipped on Linux.

---

## Usage

### Development Mode

```bash
python src/main.py
```

### Building a Windows Executable

```powershell
# Option 1: Use the build script (auto-increments version)
.\build_and_run.ps1

# Option 2: Build manually with PyInstaller
python -m PyInstaller auto_accept.spec --noconfirm
```

The resulting `auto_accept.exe` will be in the `dist/` directory. It is a standalone executable — no Python installation needed on the target machine.

### What Happens on Launch

1. **Discord** — If Discord isn't running, the app attempts to launch it automatically
2. **Dota 2** — If Dota 2 isn't running, the app launches it via Steam protocol (`steam://rungameid/570`)
3. **Detection starts** — The app captures screenshots in a loop and compares them against reference images using SSIM
4. **Match found** — When a match is detected (score above threshold), the app:
   - Plays an alert sound
   - Focuses the Dota 2 window
   - Sends a Telegram notification (if configured)
   - Automatically clicks the accept button
5. **Detection ends** — If an "AD" (ad/cooldown) screen is detected, detection stops

---

## Configuration

All settings are stored in `config.json` at the project root. Changes are saved automatically when adjusted from the UI.

### Settings Reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `alert_volume` | `float` | `1.0` | Alert sound volume (0.0 – 1.0) |
| `selected_device_id` | `int/null` | `null` | Audio output device ID (`null` = system default) |
| `always_on_top` | `bool` | `false` | Keep the app window always on top |
| `enhanced_window_focus` | `bool` | `true` | Use enhanced window focusing (Win32 API) |
| `auto_focus_on_detection` | `bool` | `true` | Auto-focus Dota 2 when a match is found |
| `brief_focus_then_restore` | `bool` | `true` | Briefly focus Dota 2 then restore previous focus |
| `focus_retry_attempts` | `int` | `3` | Number of retries for window focusing |
| `focus_delay_ms` | `int` | `150` | Delay (ms) between focus attempts |
| `ui_theme` | `string` | `"dark"` | UI theme: `"dark"`, `"light"`, or `"system"` |
| `use_modern_ui` | `bool` | `true` | Use Modern UI (`false` = classic tkinter) |
| `detection_threshold` | `float` | `0.7` | SSIM match threshold (0.0 – 1.0). Higher = stricter matching |
| `auto_detect_dota_monitor` | `bool` | `false` | Auto-detect which monitor has Dota 2 |
| `telegram_enabled` | `bool` | `false` | Enable Telegram notifications |
| `telegram_bot_token` | `string` | `""` | Your Telegram bot token from @BotFather |
| `telegram_chat_id` | `string` | `""` | Your Telegram chat ID |
| `telegram_message` | `string` | `"⚠️ Partida encontrada..."` | Message sent on match found |
| `telegram_send_screenshots` | `bool` | `true` | Send a screenshot with the notification |
| `telegram_screenshot_interval` | `int` | `60` | Minimum seconds between screenshot sends |
| `telegram_notify_events` | `bool` | `true` | Notify on start/stop events too |

### Example `config.json`

```json
{
  "alert_volume": 0.75,
  "selected_device_id": null,
  "always_on_top": false,
  "enhanced_window_focus": true,
  "auto_focus_on_detection": true,
  "brief_focus_then_restore": true,
  "focus_retry_attempts": 3,
  "focus_delay_ms": 150,
  "ui_theme": "dark",
  "use_modern_ui": true,
  "detection_threshold": 0.8,
  "auto_detect_dota_monitor": false,
  "telegram_enabled": true,
  "telegram_bot_token": "YOUR_BOT_TOKEN_HERE",
  "telegram_chat_id": "YOUR_CHAT_ID_HERE",
  "telegram_message": "⚠️ Partida encontrada no Dota 2! Aceitando automaticamente.",
  "telegram_send_screenshots": true,
  "telegram_screenshot_interval": 60,
  "telegram_notify_events": true
}
```

---

## Telegram Bot Setup

### 1. Create a Bot with @BotFather

1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)**
2. Send the command: `/newbot`
3. Choose a **display name** for your bot (e.g., `Dota2 Auto Accept`)
4. Choose a **username** (must end in `bot`, e.g., `dota2_auto_accept_bot`)
5. BotFather will reply with a **bot token** — copy it

### 2. Get Your Chat ID

1. Open Telegram and search for **[@userinfobot](https://t.me/userinfobot)**
2. Click **Start** and send any message
3. The bot will reply with your **Chat ID** — copy it

### 3. Start Your Bot

1. Search for your bot's username in Telegram
2. Click **Start** — this is required so the bot can send you messages

### 4. Configure

Paste the bot token and chat ID into `config.json`:

```json
{
  "telegram_enabled": true,
  "telegram_bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "telegram_chat_id": "987654321",
  "telegram_message": "⚠️ Partida encontrada no Dota 2! Aceitando automaticamente.",
  "telegram_send_screenshots": true,
  "telegram_screenshot_interval": 60,
  "telegram_notify_events": true
}
```

### 5. Test

Click the **"Test Telegram"** button in the UI to send a test message and verify everything works.

---

## Logging

Logs are written to `src/logs/` (development) or next to the `.exe` (bundled). Log files are named:

```
auto_accept_YYYYMMDD_HHMMSS.log
```

Log level: `DEBUG` (file) / `INFO` (console).

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **"No module named sounddevice"** | Run `pip install sounddevice` in your venv |
| **Detection not working** | Adjust `detection_threshold` in `config.json` (try `0.6` – `0.9`) |
| **Telegram not sending** | Verify bot token & chat ID; ensure you clicked "Start" on your bot |
| **Wrong monitor detected** | Set `auto_detect_dota_monitor: true` or manually select the monitor in the UI |
| **App crashes on launch** | Check `src/logs/` for detailed error output |
| **Build fails** | Ensure PyInstaller is installed: `pip install pyinstaller` |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `mss` | Fast multi-monitor screenshot capture |
| `numpy` / `opencv-python` | Image processing and template matching |
| `scikit-image` | SSIM (Structural Similarity Index) calculation |
| `Pillow` | Image format conversion |
| `pygame` | Alert sound playback |
| `sounddevice` | Audio device enumeration |
| `pyautogui` | Simulating key/mouse events |
| `customtkinter` | Modern tkinter UI |
| `psutil` | Process detection (Discord, Dota 2) |
| `requests` | Telegram Bot API HTTP calls |
| `pytesseract` | OCR support for text detection |
| `pycaw` | Windows audio control (Windows only) |
| `pygetwindow` / `pywin32` | Window focus and management (Windows only) |

---

## License

MIT License
