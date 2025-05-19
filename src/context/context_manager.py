class ContextManager:
    """
    Context Management module to maintain conversation context
    """
    def __init__(self, max_history=10):
        """
        Initialize the Context Management module
        
        Args:
            max_history: Maximum number of conversation turns to keep in history
        """
        self.max_history = max_history
        self.conversation_history = []
        self.current_context = {}
    
    def add_to_history(self, user_input, system_response, classification=None, metadata=None):
        """
        Add a conversation turn to history
        
        Args:
            user_input: User's transcribed speech
            system_response: System's response
            classification: Input classification (actionable, intent, etc.)
            metadata: Additional metadata about the turn (intent, sentiment, etc.)
        """
        if metadata is None:
            metadata = {}
            
        turn = {
            "timestamp": None,  # TODO: Add timestamp
            "user_input": user_input,
            "system_response": system_response,
            "classification": classification,
            "metadata": metadata
        }
        
        self.conversation_history.append(turn)
        
        # Maintain max history size
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def get_context(self):
        """
        Get current conversation context
        
        Returns:
            dict: Current context information including history and active context
        """
        return {
            "history": self.conversation_history,
            "current_context": self.current_context
        }
    
    def update_context(self, key, value):
        """
        Update context with new information
        
        Args:
            key: Context key
            value: Context value
        """
        self.current_context[key] = value
    
    def clear_context(self):
        """
        Clear current context
        """
        self.current_context = {}
    
    def __str__(self):
        return f"ContextManager(history_size={len(self.conversation_history)})" 