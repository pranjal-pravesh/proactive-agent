#!/usr/bin/env python3
"""
Quick TTS test to verify multiple speeches work.
"""

import time
from src.tts import TextToSpeech

def quick_test():
    print("=== Quick TTS Test ===")
    
    # Initialize TTS
    print("1. Initializing TTS...")
    tts = TextToSpeech(rate=300, volume=0.8)
    time.sleep(1)  # Give it time to initialize
    
    # Test multiple async speeches
    print("2. Testing multiple speeches...")
    
    speeches = ["First", "Second", "Third"]
    
    for i, speech in enumerate(speeches):
        print(f"   Queuing speech {i+1}: {speech}")
        result = tts.speak_async(speech)
        print(f"   Result: {result}")
        time.sleep(0.5)  # Small delay between queuing
    
    # Wait for all to complete
    print("3. Waiting for completion...")
    time.sleep(8)  # Give enough time for all speeches
    
    # Cleanup
    print("4. Shutting down...")
    tts.shutdown()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    quick_test() 