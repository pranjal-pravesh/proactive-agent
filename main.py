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

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # python-dotenv not installed, skip loading

from src.stt import SpeechToText
from src.vad import VoiceActivityDetector
from src.tts import TextToSpeech
from src.gating_classifiers import ActionableClassifier, ContextableClassifier
from src.llm.qwen_llm import QwenLLM
from src.llm.phi4_mini_llm import Phi4MiniLLM
from src.rag.memory_store import add_to_knowledge_base, retrieve_context
from src.tool_calls import ToolManager

# --- Conversation Memory Class ---
class ConversationMemory:
    """Simple conversation memory to track recent chat history"""
    
    def __init__(self, max_turns=5, log_file="memory/chat_history.txt"):
        self.max_turns = max_turns
        self.turns = []  # List of {"user": str, "assistant": str} dicts
        self.log_file = log_file
        
        # Initialize log file with header
        self._write_log_header()
    
    def _write_log_header(self):
        """Write header to the log file"""
        import os
        from datetime import datetime
        
        # Create memory directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("VOICE ASSISTANT CHAT HISTORY LOG\n")
            f.write(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
    
    def _update_log_file(self):
        """Update the entire log file with current conversation history"""
        from datetime import datetime
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n[{datetime.now().strftime('%H:%M:%S')}] CONVERSATION MEMORY UPDATE\n")
                f.write(f"Total turns stored: {len(self.turns)}/{self.max_turns}\n")
                f.write("-" * 40 + "\n")
                
                if not self.turns:
                    f.write("(No conversation history yet)\n")
                else:
                    for i, turn in enumerate(self.turns, 1):
                        f.write(f"Turn {i}:\n")
                        f.write(f"  User: {turn['user']}\n")
                        f.write(f"  Assistant: {turn['assistant']}\n")
                        f.write("\n")
                
                f.write("-" * 40 + "\n")
                f.write("END OF MEMORY UPDATE\n\n")
                f.flush()  # Force write to disk immediately
        except Exception as e:
            print(f"Warning: Could not update chat history log: {e}")
    
    def add_turn(self, user_message, assistant_response):
        """Add a conversation turn"""
        if self.max_turns > 0:
            self.turns.append({
                "user": user_message,
                "assistant": assistant_response
            })
            # Keep only the last max_turns
            if len(self.turns) > self.max_turns:
                self.turns.pop(0)
            
            # Log the update to file
            self._update_log_file()
    
    def get_history_string(self):
        """Get conversation history as a formatted string"""
        if not self.turns:
            return ""
        
        history_lines = []
        for turn in self.turns:
            history_lines.append(f"User: {turn['user']}")
            history_lines.append(f"Assistant: {turn['assistant']}")
        
        return "\n".join(history_lines)
    
    def clear(self):
        """Clear conversation memory"""
        self.turns = []
        # Log the memory clear
        from datetime import datetime
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n[{datetime.now().strftime('%H:%M:%S')}] MEMORY CLEARED\n")
                f.write("All conversation history has been reset.\n\n")
                f.flush()
        except Exception as e:
            print(f"Warning: Could not log memory clear: {e}")
    
    def get_turn_count(self):
        """Get number of stored turns"""
        return len(self.turns)

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
        
        # Initialize TTS
        tts_config = self.config.get("tts", {})
        self.tts_enabled = tts_config.get("enabled", True)
        if self.tts_enabled:
            self.console.print("[bold cyan]Initializing TTS module...[/bold cyan]")
            self.tts = TextToSpeech(
                rate=tts_config.get("rate", 200),
                volume=tts_config.get("volume", 0.9),
                voice=tts_config.get("voice"),
                console=self.console
            )
        else:
            self.tts = None
            self.console.print("[bold yellow]TTS disabled in configuration[/bold yellow]")
        
        self.console.print("[bold cyan]Initializing LLM module...[/bold cyan]")
        llm_config = self.config.get("llm", {})
        model_type = llm_config.get("model_type", "qwen3").lower()
        
        if model_type == "phi4mini":
            self.llm = Phi4MiniLLM(
                model_path=llm_config.get("model_path", "models/Phi-4-mini-instruct-Q4_K_M.gguf"),
                n_ctx=llm_config.get("n_ctx", 2048),
                n_threads=llm_config.get("n_threads", 8)
            )
        elif model_type == "qwen3":
            self.llm = QwenLLM(
                model_path=llm_config.get("model_path", "models/Qwen3-1.7B-Q4_0.gguf"),
                n_ctx=llm_config.get("n_ctx", 2048),
                n_threads=llm_config.get("n_threads", 8)
            )
        else:
            self.console.print(f"[bold red]Unknown model type: {model_type}. Defaulting to Qwen3.[/bold red]")
            self.llm = QwenLLM(
                model_path=llm_config.get("model_path", "models/Qwen3-1.7B-Q4_0.gguf"),
                n_ctx=llm_config.get("n_ctx", 2048),
                n_threads=llm_config.get("n_threads", 8)
            )
        
        self.console.print("[bold cyan]Initializing Actionable Classifier...[/bold cyan]")
        self.actionable_classifier = ActionableClassifier(
            model_path=self.config.get("gating_classifiers", {}).get("actionable_model_path", 
                      "./src/gating_classifiers/models/mobilebert-finetuned-actionable")
        )
        
        self.console.print("[bold cyan]Initializing Contextable Classifier...[/bold cyan]")
        self.contextable_classifier = ContextableClassifier(
            model_path=self.config.get("gating_classifiers", {}).get("contextable_model_path", 
                      "./src/gating_classifiers/models/mobilebert-finetuned-contextable")
        )
        
        # Audio queue and state
        self.audio_queue = queue.Queue()
        self.buffered_audio = []
        self.speech_active = False
        self.last_speech_time = time.time()
        self.last_transcript = ""
        self.last_response = ""
        self.last_actionable = None
        self.last_contextable = None
        
        # Timing information
        self.voice_detection_time = 0
        self.transcription_time = 0
        self.llm_response_time = 0
        self.total_processing_time = 0
        
        # Initialize conversation memory
        conv_memory_config = self.config.get("conversation_memory", {})
        max_turns = conv_memory_config.get("max_turns", 5)
        self.conversation_memory = ConversationMemory(max_turns=max_turns)
        self.include_history_in_prompt = conv_memory_config.get("include_in_prompt", True)
        
        # Initialize actionable sentence logger
        self._setup_actionable_logger()
        
        # Initialize tool manager
        self.console.print("[bold cyan]Initializing Tool Manager...[/bold cyan]")
        self.tool_manager = ToolManager()
        self.tools_enabled = True  # Could be made configurable
    
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
            status_text = "[bold yellow]Speech ended. Processing...[/bold yellow]"
            
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
            text.append(f"Actionable: {self.last_actionable['prediction']} " +
                       f"(Confidence: {self.last_actionable['confidence']:.2f})\n", style="yellow")
        
        if self.last_contextable:
            text.append(f"Contextable: {self.last_contextable['prediction']} " +
                       f"(Confidence: {self.last_contextable['confidence']:.2f})\n", style="yellow")
            
        text.append(f"Last response:\n", style="bold white")
        if self.last_response:
            text.append(f"{self.last_response}\n", style="green")
            
        # Add conversation memory info
        text.append(f"Conversation Memory: {self.conversation_memory.get_turn_count()}/{self.conversation_memory.max_turns} turns\n", style="magenta")
            
        # Add timing information
        text.append("\nTiming Information:\n", style="bold white")
        text.append(f"Voice Detection: {self.voice_detection_time:.2f}s\n", style="cyan")
        text.append(f"Transcription: {self.transcription_time:.2f}s\n", style="cyan")
        text.append(f"LLM Response: {self.llm_response_time:.2f}s\n", style="cyan")
        text.append(f"Total Processing: {self.total_processing_time:.2f}s\n", style="cyan")
        
        return Panel(text, title="[bold blue]Voice Assistant[/bold blue]", border_style="blue")
    
    def _process_audio_chunk(self, audio_chunk):
        """
        Process an audio chunk
        
        Args:
            audio_chunk: Audio chunk to process
        """
        audio_np = audio_chunk[:, 0]
        
        # Detect speech
        vad_start = time.time()
        speech_timestamps = self.vad.detect_speech(audio_np)
        self.voice_detection_time = time.time() - vad_start
        
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
        start_time = time.time()
        
        # Combine buffered audio chunks
        full_audio = np.concatenate(self.buffered_audio)
        
        # Transcribe
        transcribe_start = time.time()
        self.last_transcript = self.stt.transcribe(full_audio)
        self.transcription_time = time.time() - transcribe_start
        self.console.print(f"[bold green]Transcription:[/bold green] {self.last_transcript}")
        
        if self.last_transcript.strip():
            # Check for memory reset command
            if self.last_transcript.strip().lower() == "reset memory":
                self.conversation_memory.clear()
                self.console.print("[bold magenta]Conversation memory reset![/bold magenta]")
                self.last_response = "Conversation memory has been reset."
                
                # Speak the response if TTS is enabled
                if self.tts_enabled and self.tts:
                    self.tts.speak_async(self.last_response)
                
                self.total_processing_time = time.time() - start_time
                self.buffered_audio = []
                self.speech_active = False
                return
            
            # Auto-reset if we detect repetitive refusal patterns
            if len(self.conversation_memory.turns) >= 2:
                recent_responses = [turn["assistant"] for turn in self.conversation_memory.turns[-2:]]
                if all("I'm sorry, but I can't provide information" in response for response in recent_responses):
                    self.console.print("[bold yellow]Detected repetitive refusals - clearing memory to reset context[/bold yellow]")
                    self.conversation_memory.clear()
            
            # Classify if actionable
            actionable_result = self.actionable_classifier.is_actionable(self.last_transcript)
            self.last_actionable = actionable_result
            
            # Classify if contextable
            contextable_result = self.contextable_classifier.is_contextable(self.last_transcript)
            self.last_contextable = contextable_result
            
            # Log classification results
            self.console.print(f"[bold blue]Actionable Classification:[/bold blue] {actionable_result['prediction']} " +
                              f"(Confidence: {actionable_result['confidence']:.2f})")
            self.console.print(f"[bold blue]Contextable Classification:[/bold blue] {contextable_result['prediction']} " +
                              f"(Confidence: {contextable_result['confidence']:.2f})")
            
            # Only process further if transcript is actionable
            if actionable_result["actionable"]:
                # Log this actionable sentence for data collection
                self._log_actionable_sentence(self.last_transcript, actionable_result["confidence"])
                
                # Retrieve relevant contextable memory
                contexts = retrieve_context(self.last_transcript, k=5)
                context_block = "\n".join(f"- {ctx}" for ctx in contexts)
                
                # Build conversation history block
                history_block = ""
                if self.include_history_in_prompt:
                    history_str = self.conversation_memory.get_history_string()
                    if history_str:
                        history_block = f"\nConversation History:\n{history_str}\n"
                
                # Build user input with context and history
                user_input = f"""Context:
                                {context_block}
                                {history_block}
                                Question:
                                {self.last_transcript}"""
                
                llm_start = time.time()
                # Get tools prompt if tools are enabled
                tools_prompt = ""
                if self.tools_enabled:
                    tools_prompt = self.tool_manager.get_tools_prompt()
                
                llm_response, _ = self.llm.generate(
                    user_input,
                    max_tokens=self.config.get("llm", {}).get("max_tokens", 2000),
                    temperature=self.config.get("llm", {}).get("temperature", 0.7),
                    top_p=self.config.get("llm", {}).get("top_p", 0.9),
                    tools_prompt=tools_prompt
                )
                self.llm_response_time = time.time() - llm_start
                
                # Process response for tool calls
                if self.tools_enabled:
                    processed_response = self.tool_manager.process_response_with_tools(llm_response)
                    
                    if processed_response["tool_used"]:
                        # Check if tool_call exists and has the expected structure
                        tool_call = processed_response.get("tool_call", {})
                        if "tool_name" in tool_call:
                            self.console.print(f"[bold cyan]Tool Call Detected:[/bold cyan] {tool_call['tool_name']}")
                        else:
                            self.console.print(f"[bold cyan]Tool Call Detected[/bold cyan] (parsing failed)")
                        
                        # Format the response with tool result
                        response_text = processed_response["content"]
                        tool_result_text = self.tool_manager.format_tool_result_for_user(processed_response["tool_result"])
                        
                        if response_text:
                            self.last_response = f"{response_text}\n\n{tool_result_text}"
                        else:
                            self.last_response = tool_result_text
                    else:
                        self.last_response = processed_response["content"]
                else:
                    self.last_response = llm_response
                
                # Add this conversation turn to memory
                self.conversation_memory.add_turn(self.last_transcript, self.last_response)
            else:
                # For non-actionable inputs, just acknowledge
                self.last_response = "I heard you, but I'm not sure what action to take."
                self.llm_response_time = 0  # Reset LLM time since we didn't use it
                
                # Add this conversation turn to memory (even for non-actionable responses)
                self.conversation_memory.add_turn(self.last_transcript, self.last_response)
            
            # Update context only if the input is contextable
            if contextable_result["contextable"]:
                # Add to knowledge base (RAG memory)
                add_to_knowledge_base(self.last_transcript, {"timestamp": time.time()})
                self.console.print("[bold magenta]Added to context memory[/bold magenta]")
            else:
                self.console.print("[bold magenta]Not adding to context memory[/bold magenta]")
            
            self.console.print(f"[bold green]Response:[/bold green] {self.last_response}")  # Show response display
            
            # Speak the response if TTS is enabled
            if self.tts_enabled and self.tts and self.last_response:
                self.tts.speak_async(self.last_response)
        
        # Update total processing time
        self.total_processing_time = time.time() - start_time
        
        # Reset state
        self.buffered_audio = []
        self.speech_active = False
    
    def _setup_actionable_logger(self):
        """Setup logging for actionable sentences."""
        import os
        from datetime import datetime
        
        # Create memory directory if it doesn't exist
        os.makedirs("memory", exist_ok=True)
        
        # Initialize actionable sentences log file
        self.actionable_log_file = "memory/actionable_sentences.txt"
        
        # Write header if file doesn't exist
        if not os.path.exists(self.actionable_log_file):
            with open(self.actionable_log_file, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("ACTIONABLE SENTENCES DATA COLLECTION LOG\n")
                f.write(f"Log started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 70 + "\n\n")
                f.write("Format: [TIMESTAMP] CONFIDENCE=X.XX | TEXT\n\n")
    
    def _log_actionable_sentence(self, transcript: str, confidence: float):
        """
        Log an actionable sentence for data collection.
        
        Args:
            transcript: The actionable sentence
            confidence: Confidence score from the classifier
        """
        from datetime import datetime
        
        try:
            with open(self.actionable_log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] CONFIDENCE={confidence:.3f} | {transcript}\n")
                f.flush()  # Ensure immediate write
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not log actionable sentence: {e}[/yellow]")
    
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
                
                # Cleanup TTS
                if self.tts_enabled and self.tts:
                    self.console.print("[cyan]Shutting down TTS...[/cyan]")
                    self.tts.shutdown()
                
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