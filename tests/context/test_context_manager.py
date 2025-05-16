import unittest
from src.context import ContextManager

class TestContextManager(unittest.TestCase):
    def test_initialization(self):
        context_manager = ContextManager(max_history=5)
        self.assertEqual(context_manager.max_history, 5)
        self.assertEqual(context_manager.conversation_history, [])
        self.assertEqual(context_manager.current_context, {})
    
    def test_add_to_history(self):
        context_manager = ContextManager(max_history=2)
        context_manager.add_to_history("Hello", "Hi there!", None, None)
        self.assertEqual(len(context_manager.conversation_history), 1)
        
    def test_update_context(self):
        context_manager = ContextManager()
        context_manager.update_context("user_name", "John")
        self.assertEqual(context_manager.current_context["user_name"], "John")

if __name__ == '__main__':
    unittest.main() 