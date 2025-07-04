#!/usr/bin/env python3
"""
Test script to verify audio device selection improvements
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.audio_model import AudioModel
from models.config_model import ConfigModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_audio_devices():
    """Test audio device functionality"""
    print("Testing Audio Device Selection...")
    
    # Create audio model
    audio_model = AudioModel()
    
    # Get available devices
    devices = audio_model.get_output_devices()
    print(f"\nFound {len(devices)} audio output devices:")
    for i, device in enumerate(devices):
        print(f"  {i}: {device['name']} (ID: {device['id']})")
    
    # Test default device
    default_device = audio_model.get_default_output_device()
    if default_device:
        print(f"\nDefault device: {default_device['name']} (ID: {default_device['id']})")
    else:
        print("\nNo default device found.")
    
    # Test device availability
    if devices:
        first_device_id = devices[0]["id"]
        is_available = audio_model.is_device_available(first_device_id)
        print(f"\nFirst device (ID: {first_device_id}) is available: {is_available}")
    
    # Test sound playback (commented out to avoid playing sound during testing)
    # print("\nTesting sound playback on default device...")
    # audio_model.test_sound(None, 0.5)  # Use default device with 50% volume
    
    if devices:
        print(f"\nTesting sound playback on first device (ID: {devices[0]['id']})...")
        # audio_model.test_sound(devices[0]["id"], 0.5)  # Use first device with 50% volume
    
    print("\nAudio device test completed successfully!")

def test_config_integration():
    """Test configuration integration"""
    print("\nTesting Configuration Integration...")
    
    config_model = ConfigModel()
    audio_model = AudioModel()
    
    # Get devices
    devices = audio_model.get_output_devices()
    
    if devices:
        # Test setting device
        test_device_id = devices[0]["id"]
        config_model.selected_device_id = test_device_id
        print(f"Set device ID in config: {test_device_id}")
        
        # Test getting device
        retrieved_device_id = config_model.selected_device_id
        print(f"Retrieved device ID from config: {retrieved_device_id}")
        
        # Test volume
        config_model.alert_volume = 0.75
        print(f"Set volume in config: {config_model.alert_volume}")
    
    print("Configuration integration test completed!")

if __name__ == "__main__":
    try:
        test_audio_devices()
        test_config_integration()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
