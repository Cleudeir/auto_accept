"""
Bluetooth Device Discovery Tool
This script helps you find your phone's Bluetooth MAC address
"""

import asyncio
try:
    from bleak import BleakScanner
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("Bluetooth not available. Install bleak: pip install bleak")
    exit(1)

async def discover_devices():
    """Discover nearby Bluetooth devices"""
    print("Scanning for Bluetooth devices...")
    print("Make sure your phone's Bluetooth is ON and discoverable")
    print("This may take 10-15 seconds...\n")
    
    try:
        devices = await BleakScanner.discover(timeout=10.0)
        
        if devices:
            print(f"Found {len(devices)} Bluetooth devices:")
            print("-" * 50)
            for i, device in enumerate(devices, 1):
                name = device.name if device.name else "Unknown Device"
                print(f"{i:2}. Name: {name}")
                print(f"    Address: {device.address}")
                print(f"    RSSI: {device.rssi} dBm")
                print()
        else:
            print("No Bluetooth devices found.")
            print("Make sure your phone is:")
            print("- Bluetooth enabled")
            print("- In discoverable mode")
            print("- Close to your computer")
            
    except Exception as e:
        print(f"Error during discovery: {e}")

def main():
    if not BLUETOOTH_AVAILABLE:
        return
        
    print("=== Bluetooth Device Discovery ===")
    print("This tool will help you find your phone's Bluetooth address")
    print()
    
    # Run the async discovery
    asyncio.run(discover_devices())
    
    print("\n=== Instructions ===")
    print("1. Find your phone in the list above")
    print("2. Copy its Address (format: XX:XX:XX:XX:XX:XX)")
    print("3. Update dota_auto_accept.py with this address")
    print("4. Set enable_bluetooth_notifications = True")

if __name__ == "__main__":
    main()
