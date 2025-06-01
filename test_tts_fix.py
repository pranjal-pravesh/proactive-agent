#!/usr/bin/env python3
"""
Simple test script to verify TTS threading fix.
"""

import time
from src.tts import TextToSpeech

def test_tts_threading():
    """Test TTS with multiple rapid async calls to reproduce the previous error."""
    print("Testing TTS threading fix...")
    
    try:
        # Initialize TTS
        print("Initializing TTS...")
        tts = TextToSpeech(rate=250, volume=0.8)
        print("TTS initialized successfully")
        
        # Test rapid async calls (this used to cause the error)
        test_phrases = [
            "First response",
            "Second response", 
            "Third response"
        ]
        
        print("\nStarting async speech tests...")
        for i, phrase in enumerate(test_phrases):
            print(f"\n--- Test {i+1} ---")
            print(f"Queuing: {phrase}")
            result = tts.speak_async(phrase)
            print(f"Queue result: {result}")
            time.sleep(2)  # Wait between each to see if they complete
        
        # Wait for all speech to complete
        print("\nWaiting for remaining speech to complete...")
        time.sleep(3)
        
        # Test one more to see if worker is still alive
        print("\nTesting if worker is still responsive...")
        result = tts.speak_async("Final test message")
        print(f"Final test result: {result}")
        time.sleep(3)
        
        # Cleanup
        print("\nShutting down TTS...")
        tts.shutdown()
        print("TTS test completed!")
        return True
        
    except Exception as e:
        print(f"TTS test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tts_threading()
    if success:
        print("\n✅ TTS threading fix appears to be working!")
    else:
        print("\n❌ TTS threading fix needs more work.") 