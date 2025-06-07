# Bluetooth Configuration Guide for Dota Auto Accept

## Setting up Bluetooth Notifications

Your Dota Auto Accept application now supports Bluetooth notifications! Here's how to configure it:

### Step 1: Find your phone's Bluetooth MAC address

#### For Android:
1. Go to Settings > About Phone > Status
2. Look for "Bluetooth address" or "BD Address"
3. It will look like: `12:34:56:78:9A:BC`

#### For iPhone:
1. Go to Settings > General > About
2. Look for "Bluetooth" address
3. It will look like: `12:34:56:78:9A:BC`

### Step 2: Configure the application

1. Open `dota_auto_accept.py`
2. Find these lines around line 44-45:
   ```python
   self.phone_bluetooth_address = ""  # Set your phone's MAC address here
   self.enable_bluetooth_notifications = False  # Set to True when configured
   ```

3. Update them with your phone's information:
   ```python
   self.phone_bluetooth_address = "12:34:56:78:9A:BC"  # Your phone's MAC address
   self.enable_bluetooth_notifications = True  # Enable notifications
   ```

### Step 3: Install dependencies

Make sure you have the Bluetooth library installed:
```bash
pip install bleak
```

### Step 4: Pair your devices

1. Make sure your phone and PC are paired via Bluetooth
2. Keep Bluetooth enabled on both devices
3. Ensure they are within range (about 10 meters)

### How it works

When a Dota 2 match is found and accepted, the application will:
1. Send a Bluetooth notification to your phone
2. Display a timestamp and message: `[HH:MM:SS] Dota 2: Match Accepted!`
3. Print confirmation in the console

### Troubleshooting

**If Bluetooth notifications don't work:**

1. **Check pairing**: Ensure devices are properly paired
2. **Check range**: Make sure devices are close enough
3. **Check MAC address**: Verify you entered the correct Bluetooth address
4. **Check permissions**: Some phones require apps to accept Bluetooth connections

**Alternative notification methods:**

If Bluetooth doesn't work reliably, consider these alternatives:
- Pushbullet API (works over internet)
- Telegram Bot (works anywhere)
- Email notifications
- Windows notifications (local only)

### Example configuration

```python
# Example working configuration
self.phone_bluetooth_address = "A1:B2:C3:D4:E5:F6"  # Samsung Galaxy
self.enable_bluetooth_notifications = True
```

### Testing

To test if your configuration works:
1. Run the application
2. Start Dota 2
3. Click "Start" in the auto-accept tool
4. The console should show: "Bluetooth notification prepared" when a match is found

### Notes

- The current implementation uses BLE (Bluetooth Low Energy)
- For classic Bluetooth, you might need additional phone apps
- Notifications work best when devices stay connected
- Battery usage on phone will be minimal
