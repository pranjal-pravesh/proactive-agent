import unittest
import numpy as np
from unittest.mock import patch, MagicMock

from src.stt import SpeechToText

class TestSpeechToText(unittest.TestCase):
    """
    Test cases for SpeechToText class
    """
    @patch('src.stt.stt.WhisperModel')
    def test_initialization(self, mock_whisper):
        """Test proper initialization of SpeechToText"""
        stt = SpeechToText(model_size="tiny", compute_type="float16", device="cpu")
        
        mock_whisper.assert_called_once_with("tiny", compute_type="float16", device="cpu")
        self.assertEqual(stt.model_size, "tiny")
        self.assertEqual(stt.compute_type, "float16")
        self.assertEqual(stt.device, "cpu")
    
    @patch('src.stt.stt.WhisperModel')
    def test_transcribe(self, mock_whisper):
        """Test transcription functionality"""
        # Setup mock
        mock_model = MagicMock()
        mock_segments = [
            MagicMock(text="Hello"),
            MagicMock(text="world")
        ]
        mock_model.transcribe.return_value = (mock_segments, None)
        mock_whisper.return_value = mock_model
        
        # Create SpeechToText instance and call transcribe
        stt = SpeechToText()
        audio_data = np.zeros(16000)  # 1 second of silence at 16kHz
        result = stt.transcribe(audio_data)
        
        # Verify results
        mock_model.transcribe.assert_called_once_with(audio_data, language="en")
        self.assertEqual(result, "Hello world")

if __name__ == '__main__':
    unittest.main() 