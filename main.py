import time
import numpy as np
import sounddevice as sd
import queue
import yaml
import argparse
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from src.stt import SpeechToText
from src.vad import VoiceActivityDetector
from src.intent import IntentRecognizer
from src.sentiment import SentimentAnalyzer
from src.context import ContextManager
from src.executor import TaskExecutor
from src.gating_classifiers import ActionableClassifier

# --- Constants ---
DEFAULT_CONFIG_PATH = "configs/config.yaml"
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_BLOCK_DURATION = 0.5

class VoiceAssistant:
    """
    Main orchestrator for the voice assistant system
    """
    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        """
        Initialize the voice assistant with all components
        
        Args:
            config_path: Path to configuration file
        """
        self.console = Console()
        self.console.print("[bold cyan]Initializing Voice Assistant...[/bold cyan]")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize audio parameters
        self.sample_rate = self.config.get("audio", {}).get("sample_rate", DEFAULT_SAMPLE_RATE)
        self.block_duration = self.config.get("audio", {}).get("block_duration", DEFAULT_BLOCK_DURATION)
        self.block_size = int(self.sample_rate * self.block_duration)
        
        # Initialize components
        self.console.print("[bold cyan]Initializing STT module...[/bold cyan]")
        self.stt = SpeechToText(
            model_size=self.config.get("stt", {}).get("model_size", "small.en"),
            compute_type=self.config.get("stt", {}).get("compute_type", "int8"),
            device=self.config.get("stt", {}).get("device", "cpu")
        )
        
        self.console.print("[bold cyan]Initializing VAD module...[/bold cyan]")
        self.vad = VoiceActivityDetector(
            sample_rate=self.sample_rate,
            threshold=self.config.get("vad", {}).get("threshold", 0.5)
        )
        
        self.console.print("[bold cyan]Initializing Intent Recognition module...[/bold cyan]")
        self.intent_recognizer = IntentRecognizer(
            model_path=self.config.get("intent", {}).get("model_path")
        )
        
        self.console.print("[bold cyan]Initializing Sentiment Analysis module...[/bold cyan]")
        self.sentiment_analyzer = SentimentAnalyzer(
            model_path=self.config.get("sentiment", {}).get("model_path")
        )
        
        self.console.print("[bold cyan]Initializing Context Manager...[/bold cyan]")
        self.context_manager = ContextManager(
            max_history=self.config.get("context", {}).get("max_history", 10)
        )
        
        self.console.print("[bold cyan]Initializing Task Executor...[/bold cyan]")
        self.task_executor = TaskExecutor()
        
        self.console.print("[bold cyan]Initializing Actionable Classifier...[/bold cyan]")
        self.actionable_classifier = ActionableClassifier(
            model_path=self.config.get("gating_classifiers", {}).get("actionable_model_path", 
                      "./src/gating_classifiers/models/mobilebert-finetuned-actionable")
        )
        
        # Audio queue and state
        self.audio_queue = queue.Queue()
        self.buffered_audio = []
        self.speech_active = False
        self.last_speech_time = time.time()
        self.last_transcript = ""
        self.last_response = ""
        self.last_actionable = None
    
    def _load_config(self, config_path):
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            dict: Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.console.print(f"[bold red]Error loading config: {e}[/bold red]")
            return {}
    
    def _select_audio_device(self):
        """
        List and select audio input device
        
        Returns:
            int: Selected device index
        """
        self.console.print("[bold cyan]Available audio input devices:[/bold cyan]")
        input_devices = []
        for idx, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                input_devices.append(idx)
                self.console.print(f"[green]{idx}[/green]: {device['name']}")
        
        device_index = None
        while device_index not in input_devices:
            try:
                device_index = int(self.console.input("[bold yellow]Select microphone device index:[/bold yellow] "))
                if device_index not in input_devices:
                    self.console.print("[red]Invalid device index, please try again.[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid integer.[/red]")
        
        return device_index
    
    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback for audio input stream
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Time information
            status: Status information
        """
        if status:
            self.console.log(f"[yellow]Audio stream status: {status}[/yellow]")
        self.audio_queue.put(indata.copy())
    
    def _render_panel(self):
        """
        Render information panel for live display
        
        Returns:
            Panel: Rich panel with status information
        """
        status_text = "Listening for speech..." if not self.speech_active else "[bold green]Speech detected! Buffering...[/bold green]"
        if self.speech_active and time.time() - self.last_speech_time > 1.0:
            status_text = "[bold yellow]Speech ended. Transcribing...[/bold yellow]"
            
        text = Text()
        text.append(f"Status: {status_text}\n", style="bold magenta")
        
        if self.buffered_audio:
            text.append(f"Buffered audio length: {sum(len(chunk) for chunk in self.buffered_audio)} samples\n", style="cyan")
        else:
            text.append("Buffered audio length: 0 samples\n", style="cyan")
        
        text.append(f"Last transcript:\n", style="bold white")
        if self.last_transcript:
            text.append(f"{self.last_transcript}\n", style="bright_white")
        else:
            text.append("None yet\n", style="dim")
        
        if self.last_actionable:
            text.append(f"Classification: {self.last_actionable['prediction']} " +
                       f"(Confidence: {self.last_actionable['confidence']:.2f})\n", style="yellow")
            
        text.append(f"Last response:\n", style="bold white")
        if self.last_response:
            text.append(f"{self.last_response}\n", style="green")
        
        return Panel(text, title="[bold blue]Voice Assistant[/bold blue]", border_style="blue")
    
    def _process_audio_chunk(self, audio_chunk):
        """
        Process an audio chunk
        
        Args:
            audio_chunk: Audio chunk to process
        """
        audio_np = audio_chunk[:, 0]
        
        # Detect speech
        speech_timestamps = self.vad.detect_speech(audio_np)
        
        # Update speech state and buffer
        if speech_timestamps:
            self.buffered_audio.append(audio_np)
            self.speech_active = True
            self.last_speech_time = time.time()
        elif self.speech_active and time.time() - self.last_speech_time > 1.0:
            # Speech ended, process
            self._process_speech()
    
    def _process_speech(self):
        """
        Process buffered speech audio
        """
        self.console.print("[bold yellow]Speech ended. Processing...[/bold yellow]")
        
        # Combine buffered audio chunks
        full_audio = np.concatenate(self.buffered_audio)
        
        # Transcribe
        self.last_transcript = self.stt.transcribe(full_audio)
        self.console.print(f"[bold green]Transcription:[/bold green] {self.last_transcript}")
        
        if self.last_transcript.strip():
            # Classify if actionable
            actionable_result = self.actionable_classifier.is_actionable(self.last_transcript)
            self.last_actionable = actionable_result
            
            # Log classification result
            self.console.print(f"[bold blue]Actionable Classification:[/bold blue] {actionable_result['prediction']} " +
                              f"(Confidence: {actionable_result['confidence']:.2f})")
            
            # Only process further if transcript is actionable
            if actionable_result["actionable"]:
                # Recognize intent
                intent_data = self.intent_recognizer.recognize_intent(self.last_transcript)
                
                # Analyze sentiment
                sentiment_data = self.sentiment_analyzer.analyze_sentiment(self.last_transcript)
                
                # Execute task based on intent
                result = self.task_executor.execute_task(intent_data, self.context_manager.get_context())
                
                # Update response
                self.last_response = result.get("response", "I processed that, but I'm not sure how to respond.")
            else:
                self.last_response = "That doesn't seem like a command or request I can act on."
            
            # Update context
            self.context_manager.add_to_history(
                self.last_transcript, 
                self.last_response,
                actionable_result.get("prediction", "Unknown"),
                {}  # We can pass the intent and sentiment later if needed
            )
            
            self.console.print(f"[bold green]Response:[/bold green] {self.last_response}")
        
        # Reset state
        self.buffered_audio = []
        self.speech_active = False
    
    def run(self):
        """
        Run the voice assistant
        """
        # Select audio device
        device_index = self._select_audio_device()
        
        # Start audio stream
        self.console.print(f"[bold green]Starting audio stream on device {device_index}...[/bold green]")
        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.block_size,
            device=device_index,
            callback=self._audio_callback
        )
        stream.start()
        
        # Main loop with live UI
        with Live(self._render_panel(), refresh_per_second=4, console=self.console) as live:
            try:
                while True:
                    audio_chunk = self.audio_queue.get()
                    self._process_audio_chunk(audio_chunk)
                    live.update(self._render_panel())
            except KeyboardInterrupt:
                self.console.print("\n[bold red]Stopping Voice Assistant...[/bold red]")
                stream.stop()
                stream.close()

def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description="Voice Assistant")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="Path to config file")
    args = parser.parse_args()
    
    assistant = VoiceAssistant(config_path=args.config)
    assistant.run()

if __name__ == "__main__":
    main() 