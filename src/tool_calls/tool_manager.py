import json
import re
from typing import Dict, Any, List, Optional
from .calculator import Calculator
from .weather import WeatherChecker
from .calendar import CalendarScheduler
from .search import WebSearcher
from .file_manager import FileManager

class ToolManager:
    """Manages tool calling integration with LLM"""
    
    def __init__(self):
        self.tools = {
            "calculator": Calculator,
            "weather_checker": WeatherChecker,
            "web_searcher": WebSearcher,
            "file_manager": FileManager
        }
        # Calendar scheduler needs instance for state management
        self.calendar_scheduler = CalendarScheduler()
        self.tools["calendar_scheduler"] = self.calendar_scheduler
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for LLM system prompt"""
        tool_descriptions = []
        
        for tool_name, tool_class in self.tools.items():
            if tool_name == "calendar_scheduler":
                tool_info = tool_class.get_tool_info()
            else:
                tool_info = tool_class.get_tool_info()
            tool_descriptions.append(tool_info)
        
        return tool_descriptions
    
    def get_tools_prompt(self) -> str:
        """Generate tools section for LLM system prompt"""
        tools = self.get_available_tools()
        
        prompt = """

AVAILABLE TOOLS:
You have access to the following tools. When a user's request requires using a tool, respond with a tool call in this exact format:

<tool_call>
{
    "tool_name": "tool_name_here",
    "parameters": {
        "param1": "value1",
        "param2": "value2"
    }
}
</tool_call>

Available tools:

"""
        
        for tool in tools:
            prompt += f"**{tool['name']}**: {tool['description']}\n"
            prompt += "Parameters:\n"
            
            properties = tool['parameters']['properties']
            required = tool['parameters'].get('required', [])
            
            for param_name, param_info in properties.items():
                required_mark = " (required)" if param_name in required else ""
                param_type = param_info.get('type', 'string')
                param_desc = param_info.get('description', '')
                
                prompt += f"  - {param_name} ({param_type}){required_mark}: {param_desc}\n"
                
                if 'enum' in param_info:
                    prompt += f"    Options: {', '.join(param_info['enum'])}\n"
            
            prompt += "\n"
        
        prompt += """
IMPORTANT TOOL CALLING RULES:
1. ONLY use a tool when the user's request specifically requires tool functionality
2. For simple questions that don't need tools, respond normally without tool calls
3. Use the exact JSON format shown above for tool calls
4. Always validate that required parameters are provided
5. If a tool call fails, explain the error and suggest alternatives

Examples:
- "What's 15 + 27?" -> Use calculator tool
- "What's the weather like?" -> Use weather_checker tool
- "Schedule a meeting tomorrow" -> Use calendar_scheduler tool
- "How are you today?" -> Respond normally, no tool needed
"""
        
        return prompt
    
    def parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse tool call from LLM response"""
        # Look for tool call pattern
        tool_call_pattern = r'<tool_call>\s*(\{[^}]+\})\s*</tool_call>'
        match = re.search(tool_call_pattern, response, re.DOTALL)
        
        if not match:
            return None
        
        try:
            tool_call_json = match.group(1)
            tool_call = json.loads(tool_call_json)
            
            # Validate tool call structure
            if "tool_name" not in tool_call or "parameters" not in tool_call:
                return {"error": "Invalid tool call format. Must include 'tool_name' and 'parameters'"}
            
            return tool_call
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON in tool call: {str(e)}"}
    
    def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return results"""
        if "error" in tool_call:
            return tool_call
        
        tool_name = tool_call.get("tool_name")
        parameters = tool_call.get("parameters", {})
        
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            tool = self.tools[tool_name]
            
            # Execute tool with parameters
            if tool_name == "calendar_scheduler":
                # Instance method for calendar
                result = tool.execute(**parameters)
            else:
                # Static method for other tools
                result = tool.execute(**parameters)
            
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result,
                "success": "error" not in result
            }
            
        except Exception as e:
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "error": f"Tool execution error: {str(e)}",
                "success": False
            }
    
    def process_response_with_tools(self, llm_response: str) -> Dict[str, Any]:
        """Process LLM response, execute any tool calls, and return formatted result"""
        # Check if response contains tool call
        tool_call = self.parse_tool_call(llm_response)
        
        if tool_call is None:
            # No tool call, return normal response
            return {
                "type": "normal_response",
                "content": llm_response,
                "tool_used": False
            }
        
        # Execute tool call
        tool_result = self.execute_tool_call(tool_call)
        
        # Remove tool call from response text
        cleaned_response = re.sub(r'<tool_call>.*?</tool_call>', '', llm_response, flags=re.DOTALL).strip()
        
        return {
            "type": "tool_response",
            "content": cleaned_response,
            "tool_used": True,
            "tool_call": tool_call,
            "tool_result": tool_result
        }
    
    def format_tool_result_for_user(self, tool_result: Dict[str, Any]) -> str:
        """Format tool execution result for user display"""
        if not tool_result.get("success", False):
            return f"❌ Tool Error: {tool_result.get('error', 'Unknown error')}"
        
        tool_name = tool_result.get("tool_name", "unknown")
        result = tool_result.get("result", {})
        
        if tool_name == "calculator":
            if "calculation" in result:
                return f"🧮 {result['calculation']}"
            elif "result" in result:
                return f"🧮 Result: {result['result']}"
        
        elif tool_name == "weather_checker":
            if "summary" in result:
                return f"🌤️ {result['summary']}"
        
        elif tool_name == "calendar_scheduler":
            if "message" in result:
                return f"📅 {result['message']}"
        
        elif tool_name == "web_searcher":
            if "summary" in result:
                return f"🔍 {result['summary']}"
            
        elif tool_name == "file_manager":
            if "message" in result:
                return f"📁 {result['message']}"
        
        # Fallback: return raw result
        return f"🔧 {tool_name}: {json.dumps(result, indent=2)}" 