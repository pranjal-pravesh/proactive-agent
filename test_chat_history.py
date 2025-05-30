#!/usr/bin/env python3
"""
Test script to demonstrate chat history logging
"""

import sys
import os
sys.path.append('.')

# Import the ConversationMemory class
import importlib.util
spec = importlib.util.spec_from_file_location("main", "main.py")
main_module = importlib.util.module_from_spec(spec)

# Mock the required imports for the test
class MockConsole:
    def print(self, *args, **kwargs):
        pass

# Add mock objects to main module
main_module.Console = lambda: MockConsole()
main_module.Panel = lambda: None
main_module.Text = lambda: None
main_module.Live = lambda: None
main_module.sd = None
main_module.queue = None
main_module.yaml = None
main_module.argparse = None
main_module.time = None
main_module.np = None

# Import other necessary modules
from datetime import datetime

# Define ConversationMemory class directly for testing
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
        # Create memory directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("VOICE ASSISTANT CHAT HISTORY LOG\n")
            f.write(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
    
    def _update_log_file(self):
        """Update the entire log file with current conversation history"""
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

def test_chat_history_logging():
    """Test the chat history logging functionality"""
    
    print("Testing Chat History Logging...")
    print("=" * 40)
    
    # Create a test conversation memory with smaller max_turns
    memory = ConversationMemory(max_turns=3, log_file="memory/chat_history.txt")
    print("✅ Created ConversationMemory with logging")
    
    # Add some test conversations
    test_conversations = [
        ("What is 2 + 2?", "🧮 **2 + 2 = 4**"),
        ("Calculate the area of a circle with radius 5", "🧮 **pi*5^2 = 78.539816**"),
        ("What's 7 factorial?", "🧮 **7! = 5040**"),
        ("What is the square root of 144?", "🧮 **sqrt(144) = 12**"),
        ("Calculate 10 to the power of 3", "🧮 **10^3 = 1000**"),
    ]
    
    print(f"\nAdding {len(test_conversations)} conversation turns...")
    for i, (user_msg, assistant_msg) in enumerate(test_conversations, 1):
        print(f"  Adding turn {i}: '{user_msg[:30]}...'")
        memory.add_turn(user_msg, assistant_msg)
        
        # Small delay to show different timestamps
        import time
        time.sleep(0.1)
    
    print(f"\n✅ All conversations added to memory")
    print(f"✅ Check 'memory/chat_history.txt' to see the live updates!")
    print(f"✅ Memory currently holds {memory.get_turn_count()}/{memory.max_turns} turns")
    
    # Test memory clear
    print(f"\nTesting memory clear...")
    memory.clear()
    print(f"✅ Memory cleared - check the log file for the clear event")

if __name__ == "__main__":
    test_chat_history_logging() 