import torch
import numpy as np
from faster_whisper import WhisperModel

class SpeechToText:
    def __init__(self, model_size="small.en", compute_type="int8", device="cpu", sample_rate=16000):
        """
        Initialize the Speech-to-Text module with Whisper model
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            compute_type: Computation type (float32, float16, int8)
            device: Device to run the model on (cpu, cuda)
            sample_rate: Audio sample rate
        """
        self.model_size = model_size
        self.compute_type = compute_type
        self.device = device
        self.sample_rate = sample_rate
        
        # Load Whisper model
        self.model = WhisperModel(model_size, compute_type=compute_type, device=device)
    
    def transcribe(self, audio_data):
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Numpy array of audio samples
            
        Returns:
            str: Transcribed text
        """
        segments, _ = self.model.transcribe(audio_data, language="en")
        return " ".join(segment.text for segment in segments).strip()
    
    def __str__(self):
        return f"SpeechToText(model={self.model_size}, device={self.device})" 