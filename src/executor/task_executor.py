class TaskExecutor:
    """
    Task Executor module to perform actions based on recognized intents
    """
    def __init__(self):
        """
        Initialize the Task Executor module
        """
        self.registered_tasks = {}
    
    def register_task(self, intent_name, handler_func):
        """
        Register a task handler for a specific intent
        
        Args:
            intent_name: Name of the intent to handle
            handler_func: Function to call when intent is recognized
        """
        self.registered_tasks[intent_name] = handler_func
    
    def execute_task(self, intent_data, context=None):
        """
        Execute a task based on recognized intent
        
        Args:
            intent_data: Intent data including intent name and entities
            context: Current conversation context
            
        Returns:
            dict: Result of task execution
        """
        intent_name = intent_data.get("intent", "unknown")
        
        if intent_name in self.registered_tasks:
            handler = self.registered_tasks[intent_name]
            return handler(intent_data, context)
        else:
            return {
                "success": False,
                "message": f"No handler registered for intent: {intent_name}",
                "response": "I'm not sure how to handle that request."
            }
    
    def get_available_tasks(self):
        """
        Get list of registered tasks
        
        Returns:
            list: Names of registered tasks/intents
        """
        return list(self.registered_tasks.keys())
    
    def __str__(self):
        return f"TaskExecutor(tasks={len(self.registered_tasks)})" 