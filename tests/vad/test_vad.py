import unittest
import numpy as np
import torch
from unittest.mock import patch, MagicMock

from src.vad import VoiceActivityDetector

class TestVoiceActivityDetector(unittest.TestCase):
    """
    Test cases for VoiceActivityDetector class
    """
    @patch('src.vad.vad.torch.hub')
    def test_initialization(self, mock_torch_hub):
        """Test proper initialization of VoiceActivityDetector"""
        # Setup mock
        mock_model = MagicMock()
        mock_utils = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_torch_hub.load.return_value = (mock_model, mock_utils)
        
        # Create VoiceActivityDetector instance
        vad = VoiceActivityDetector(sample_rate=8000, threshold=0.7)
        
        # Verify initialization
        mock_torch_hub.load.assert_called_once_with(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False,
            verbose=False
        )
        self.assertEqual(vad.sample_rate, 8000)
        self.assertEqual(vad.threshold, 0.7)
        self.assertEqual(vad.model, mock_model)
        self.assertEqual(vad.get_speech_timestamps, mock_utils[0])
    
    @patch('src.vad.vad.torch.hub')
    def test_detect_speech(self, mock_torch_hub):
        """Test speech detection functionality"""
        # Setup mock
        mock_model = MagicMock()
        mock_get_speech_timestamps = MagicMock()
        mock_get_speech_timestamps.return_value = [{"start": 100, "end": 500}]
        mock_utils = [mock_get_speech_timestamps, MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_torch_hub.load.return_value = (mock_model, mock_utils)
        
        # Create VoiceActivityDetector instance and call detect_speech
        vad = VoiceActivityDetector()
        audio_chunk = np.zeros(1600)  # 0.1 second of silence at 16kHz
        result = vad.detect_speech(audio_chunk)
        
        # Verify results
        self.assertTrue(torch.equal.called)  # Verify torch.from_numpy was called
        mock_get_speech_timestamps.assert_called_once()
        self.assertEqual(result, [{"start": 100, "end": 500}])

if __name__ == '__main__':
    unittest.main()