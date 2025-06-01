"""
Test module for Text-to-Speech functionality.
"""

import time
import pytest
from src.tts import TextToSpeech


class TestTextToSpeech:
    """Test cases for TextToSpeech class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tts = TextToSpeech(rate=250, volume=0.8)
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'tts') and self.tts:
            self.tts.shutdown()
    
    def test_initialization(self):
        """Test TTS engine initialization."""
        assert self.tts._initialized is True
        assert self.tts.rate == 250
        assert self.tts.volume == 0.8
    
    def test_text_cleaning(self):
        """Test text cleaning functionality."""
        # Test basic cleaning
        dirty_text = "Hello  *world*  #testing_underscore"
        cleaned = self.tts._clean_text(dirty_text)
        assert cleaned == "Hello world testing underscore"
        
        # Test abbreviation replacement
        abbrev_text = "Dr. Smith vs. Mr. Jones, e.g. testing"
        cleaned = self.tts._clean_text(abbrev_text)
        assert "Doctor Smith versus Mister Jones, for example testing" == cleaned
    
    def test_speak_async(self):
        """Test asynchronous speech."""
        result = self.tts.speak_async("Testing asynchronous speech")
        assert result is True
        
        # Test with empty text
        result = self.tts.speak_async("")
        assert result is False
    
    def test_speak_blocking(self):
        """Test blocking speech."""
        start_time = time.time()
        result = self.tts.speak("Short test")
        duration = time.time() - start_time
        
        assert result is True
        # Should take some time for blocking speech
        assert duration > 0.1
    
    def test_voice_management(self):
        """Test voice-related functionality."""
        # Test getting available voices
        voices = self.tts.get_voices()
        assert isinstance(voices, list)
        
        # Test rate setting
        result = self.tts.set_rate(150)
        assert result is True
        assert self.tts.rate == 150
        
        # Test volume setting
        result = self.tts.set_volume(0.5)
        assert result is True
        assert self.tts.volume == 0.5
    
    def test_speaking_state(self):
        """Test speaking state management."""
        # Initially not speaking
        assert self.tts.is_speaking() is False
        
        # Start async speech
        self.tts.speak_async("Testing speaking state")
        
        # Should be speaking or finished quickly
        # (timing dependent, so we just check it doesn't crash)
        self.tts.is_speaking()
    
    def test_stop_functionality(self):
        """Test stop functionality."""
        # Start speech
        self.tts.speak_async("This is a longer speech that we will interrupt")
        
        # Stop it
        self.tts.stop()
        
        # Should not be speaking after stop
        time.sleep(0.2)  # Small delay
        assert self.tts.is_speaking() is False


def test_tts_integration():
    """Integration test for TTS with voice assistant workflow."""
    tts = TextToSpeech(rate=300, volume=0.7)
    
    try:
        # Simulate assistant responses
        responses = [
            "Hello! How can I help you today?",
            "I understand your question about the weather.",
            "The temperature is 25 degrees Celsius.",
            "Is there anything else I can help you with?"
        ]
        
        for response in responses:
            result = tts.speak_async(response)
            assert result is True
            time.sleep(0.1)  # Small delay between responses
        
        # Wait a bit for speech to process
        time.sleep(1.0)
        
    finally:
        tts.shutdown()


if __name__ == "__main__":
    # Run basic test
    tts = TextToSpeech()
    
    print("Testing TTS functionality...")
    
    # Test basic speech
    print("Speaking: Hello, this is a test of the text-to-speech system.")
    tts.speak("Hello, this is a test of the text-to-speech system.")
    
    # Test async speech
    print("Speaking async: This is asynchronous speech.")
    tts.speak_async("This is asynchronous speech.")
    
    # Wait for completion
    time.sleep(3)
    
    # Test voice listing
    voices = tts.get_voices()
    print(f"Available voices: {len(voices)}")
    for voice in voices[:3]:  # Show first 3 voices
        print(f"  - {voice['name']} ({voice['id']})")
    
    # Cleanup
    tts.shutdown()
    print("TTS test completed!") 