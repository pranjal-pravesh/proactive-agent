import torch
import numpy as np

class VoiceActivityDetector:
    """
    Voice Activity Detection module using Silero VAD
    """
    def __init__(self, sample_rate=16000, threshold=0.5):
        """
        Initialize the VAD module
        
        Args:
            sample_rate: Audio sample rate
            threshold: Voice detection threshold
        """
        self.sample_rate = sample_rate
        self.threshold = threshold
        
        # Load Silero VAD model
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False,
            verbose=False
        )
        self.get_speech_timestamps = utils[0]
    
    def detect_speech(self, audio_chunk):
        """
        Detect if speech is present in the audio chunk
        
        Args:
            audio_chunk: Numpy array of audio samples
            
        Returns:
            list: Timestamps of detected speech segments
        """
        audio_tensor = torch.from_numpy(audio_chunk).float()
        speech_timestamps = self.get_speech_timestamps(
            audio_tensor, 
            self.model, 
            sampling_rate=self.sample_rate, 
            threshold=self.threshold
        )
        return speech_timestamps
    
    def __str__(self):
        return f"VoiceActivityDetector(threshold={self.threshold})" 