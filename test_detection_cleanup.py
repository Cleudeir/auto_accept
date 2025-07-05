#!/usr/bin/env python3
"""
Test detection model after removing long_time and watch-game
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.detection_model import DetectionModel

def test_detection_model():
    """Test the detection model after cleanup"""
    print("Detection Model Cleanup Test")
    print("=" * 35)
    
    # Create detection model
    detection_model = DetectionModel()
    
    # Check reference images
    refs = detection_model.reference_images
    print(f"📋 Reference images loaded: {len(refs)}")
    for name, path in refs.items():
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"   {status} {name}: {os.path.basename(path)}")
    
    # Verify removed patterns
    removed_patterns = ["long_time", "watch-game"]
    print(f"\n🗑️  Removed patterns:")
    for pattern in removed_patterns:
        if pattern not in refs:
            print(f"   ✅ {pattern}: Successfully removed")
        else:
            print(f"   ❌ {pattern}: Still present!")
    
    # Check remaining patterns
    remaining_patterns = ["dota", "dota2_plus", "read_check", "ad"]
    print(f"\n📦 Remaining patterns:")
    for pattern in remaining_patterns:
        if pattern in refs:
            print(f"   ✅ {pattern}: Present")
        else:
            print(f"   ❌ {pattern}: Missing!")
    
    print(f"\n📊 Summary:")
    print(f"   - Total reference images: {len(refs)}")
    print(f"   - Expected count: 4 (dota, dota2_plus, read_check, ad)")
    print(f"   - Removed: long_time, watch-game")
    
    if len(refs) == 4 and all(p in refs for p in remaining_patterns):
        print(f"   🎯 Cleanup successful!")
    else:
        print(f"   ⚠️  Issues detected")

if __name__ == "__main__":
    test_detection_model()
