"""
Text-to-Speech implementation using pyttsx3.

Simple, direct implementation based on working reference code.
"""

import pyttsx3
import threading
import time
from typing import Optional, Dict, Any, List
from rich.console import Console


class TextToSpeech:
    """
    Simple, direct Text-to-Speech engine using pyttsx3.
    Based on proven working implementation.
    """
    
    def __init__(self, 
                 rate: int = 200,
                 volume: float = 0.9,
                 voice: Optional[str] = None,
                 console: Optional[Console] = None):
        """
        Initialize TTS engine.
        
        Args:
            rate: Speech rate in words per minute (default: 200)
            volume: Volume level 0.0 to 1.0 (default: 0.9)
            voice: Voice ID to use (None for default)
            console: Rich console for logging
        """
        self.console = console or Console()
        self.rate = rate
        self.volume = volume
        self.voice = voice
        
        # Engine state
        self._engine = None
        self._initialized = False
        
        # Initialize the engine
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the pyttsx3 engine."""
        try:
            self.console.print("[cyan]Initializing TTS engine...[/cyan]")
            
            # Create engine instance
            self._engine = pyttsx3.init()
            
            # Set properties
            self._engine.setProperty('rate', self.rate)
            self._engine.setProperty('volume', self.volume)
            
            # Set voice if specified
            if self.voice:
                voices = self._engine.getProperty('voices')
                for voice in voices:
                    if self.voice.lower() in voice.id.lower():
                        self._engine.setProperty('voice', voice.id)
                        break
            
            self._initialized = True
            self.console.print("[green]TTS engine initialized successfully[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Failed to initialize TTS engine: {e}[/red]")
            self._initialized = False
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Speak the given text using the simple, proven approach.
        Always synchronous like the working reference code.
        
        Args:
            text: Text to speak
            blocking: Ignored - always blocks (like reference code)
            
        Returns:
            bool: True if speech was completed successfully
        """
        if not self._initialized or not self._engine:
            self.console.print("[yellow]TTS not initialized, skipping speech[/yellow]")
            return False
        
        if not text or not text.strip():
            return False
        
        try:
            # Clean the text
            cleaned_text = self._clean_text(text)
            if not cleaned_text:
                return False
            
            self.console.print(f"[cyan]TTS speaking: '{cleaned_text[:50]}...'[/cyan]")
            
            # Direct synchronous approach - exactly like the working reference code
            # No threading, no async - just like: engine.say(response); engine.runAndWait()
            self._engine.say(cleaned_text)
            self._engine.runAndWait()
            
            self.console.print(f"[green]TTS completed: '{cleaned_text[:30]}...'[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]TTS speak error: {e}[/red]")
            return False
    
    def speak_async(self, text: str) -> bool:
        """
        Speak text "asynchronously" - but actually synchronous like reference code.
        
        Args:
            text: Text to speak
            
        Returns:
            bool: True if speech was completed successfully
        """
        # Just call the synchronous speak method
        # This matches the reference code behavior
        return self.speak(text, blocking=True)
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better TTS output."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = " ".join(text.split())
        
        # Remove or replace problematic characters
        cleaned = cleaned.replace("*", "")  # Remove asterisks
        cleaned = cleaned.replace("#", "")  # Remove hashtags
        cleaned = cleaned.replace("_", " ")  # Replace underscores with spaces
        
        # Handle common abbreviations
        replacements = {
            "e.g.": "for example",
            "i.e.": "that is",
            "etc.": "and so on",
            "vs.": "versus",
            "Dr.": "Doctor",
            "Mr.": "Mister",
            "Mrs.": "Misses",
            "Ms.": "Miss",
        }
        
        for abbrev, full in replacements.items():
            cleaned = cleaned.replace(abbrev, full)
        
        return cleaned.strip()
    
    def stop(self):
        """Stop current speech."""
        try:
            if self._engine:
                self._engine.stop()
        except Exception as e:
            self.console.print(f"[yellow]TTS stop warning: {e}[/yellow]")
    
    def is_speaking(self) -> bool:
        """Check if TTS is currently speaking."""
        return False  # Simplified implementation
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """Get available voices."""
        if not self._initialized or not self._engine:
            return []
        
        try:
            voices = self._engine.getProperty('voices')
            voice_list = []
            
            for voice in voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown')
                }
                voice_list.append(voice_info)
            
            return voice_list
            
        except Exception as e:
            self.console.print(f"[yellow]Error getting voices: {e}[/yellow]")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """Set the voice by ID."""
        if not self._initialized or not self._engine:
            return False
        
        try:
            self._engine.setProperty('voice', voice_id)
            self.voice = voice_id
            return True
        except Exception as e:
            self.console.print(f"[red]Error setting voice: {e}[/red]")
            return False
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate."""
        if not self._initialized or not self._engine:
            return False
        
        try:
            self._engine.setProperty('rate', rate)
            self.rate = rate
            return True
        except Exception as e:
            self.console.print(f"[red]Error setting rate: {e}[/red]")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Set speech volume."""
        if not self._initialized or not self._engine:
            return False
        
        try:
            volume = max(0.0, min(1.0, volume))  # Clamp to valid range
            self._engine.setProperty('volume', volume)
            self.volume = volume
            return True
        except Exception as e:
            self.console.print(f"[red]Error setting volume: {e}[/red]")
            return False
    
    def shutdown(self):
        """Clean shutdown of TTS engine."""
        try:
            self.console.print("[cyan]TTS shutting down...[/cyan]")
            
            # Stop any current speech
            self.stop()
            
            # Cleanup engine
            if self._engine:
                try:
                    self._engine.stop()
                except:
                    pass
            
            self._initialized = False
            self.console.print("[cyan]TTS engine shutdown complete[/cyan]")
            
        except Exception as e:
            self.console.print(f"[yellow]TTS shutdown warning: {e}[/yellow]")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.shutdown()
        except:
            pass 