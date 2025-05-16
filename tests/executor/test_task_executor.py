import unittest
from unittest.mock import MagicMock

from src.executor import TaskExecutor

class TestTaskExecutor(unittest.TestCase):
    def test_initialization(self):
        """Test proper initialization of TaskExecutor"""
        executor = TaskExecutor()
        self.assertEqual(executor.registered_tasks, {})
        
    def test_register_task(self):
        """Test registering task handlers"""
        executor = TaskExecutor()
        
        # Create mock handler
        mock_handler = MagicMock()
        
        # Register task
        executor.register_task("test_intent", mock_handler)
        
        # Verify task is registered
        self.assertIn("test_intent", executor.registered_tasks)
        self.assertEqual(executor.registered_tasks["test_intent"], mock_handler)
    
    def test_execute_task_registered(self):
        """Test executing a registered task"""
        executor = TaskExecutor()
        
        # Create mock handler that returns a response
        mock_response = {"success": True, "message": "Task executed", "response": "Done"}
        mock_handler = MagicMock(return_value=mock_response)
        
        # Register task
        executor.register_task("test_intent", mock_handler)
        
        # Execute task
        intent_data = {"intent": "test_intent", "entities": {"param": "value"}}
        context = {"test": "context"}
        result = executor.execute_task(intent_data, context)
        
        # Verify handler was called with correct parameters
        mock_handler.assert_called_once_with(intent_data, context)
        
        # Verify result
        self.assertEqual(result, mock_response)
    
    def test_execute_task_not_registered(self):
        """Test executing an unregistered task"""
        executor = TaskExecutor()
        
        # Execute non-existent task
        intent_data = {"intent": "unknown_intent", "entities": {}}
        result = executor.execute_task(intent_data)
        
        # Verify default response for unknown intent
        self.assertFalse(result["success"])
        self.assertIn("No handler registered", result["message"])
        self.assertIn("not sure how to handle", result["response"])
    
    def test_get_available_tasks(self):
        """Test getting list of available tasks"""
        executor = TaskExecutor()
        
        # Register some tasks
        executor.register_task("intent1", MagicMock())
        executor.register_task("intent2", MagicMock())
        
        # Get available tasks
        tasks = executor.get_available_tasks()
        
        # Verify tasks
        self.assertEqual(len(tasks), 2)
        self.assertIn("intent1", tasks)
        self.assertIn("intent2", tasks)

if __name__ == '__main__':
    unittest.main() 