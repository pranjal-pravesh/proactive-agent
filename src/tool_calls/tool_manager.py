import json
import re
from typing import Dict, Any, List, Optional
from .calculator import Calculator
from .weather import WeatherChecker
from .calendar import CalendarScheduler

class ToolManager:
    """Manages tool calling integration with LLM"""
    
    def __init__(self):
        self.tools = {
            "calculator": Calculator,
            "weather_checker": WeatherChecker,
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

CRITICAL FORMATTING RULES:
1. ALWAYS wrap the JSON with <tool_call> and </tool_call> tags
2. For calculator: PRESERVE units like "degrees" in expressions (e.g., "sin(59 degrees)" not "sin(59)")
3. Use exact mathematical notation as spoken by the user

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
3. Use the EXACT JSON format shown above for tool calls - MUST include "tool_name" and "parameters"
4. ALWAYS wrap tool calls with <tool_call> and </tool_call> tags
5. Always validate that required parameters are provided
6. If a tool call fails, explain the error and suggest alternatives
7. For calculator: PRESERVE mathematical units (degrees, radians, etc.) in expressions

SPECIFIC TOOL USAGE GUIDELINES:

CALCULATOR TOOL - Use ONLY for:
- Mathematical calculations, equations, expressions
- Arithmetic operations (+, -, *, /, ^, sqrt, etc.)
- Trigonometric functions (sin, cos, tan with degrees/radians)
- Scientific calculations (logarithms, factorials, etc.)
- When user asks "calculate", "compute", "what's X + Y", etc.

WEATHER TOOL - Use ONLY for:
- Current weather conditions ("what's the weather", "temperature", "is it raining")
- Weather-related questions ("how hot is it", "weather forecast", "current conditions")
- Location-specific weather ("weather in London", "temperature in Tokyo")
- DO NOT use for: general location questions, travel info, or non-weather topics

CALENDAR TOOL - Use ONLY for:
- Scheduling meetings or events ("schedule a meeting", "book appointment")
- Calendar management ("list my events", "cancel meeting")
- Time-based planning activities

DO NOT USE TOOLS for:
- General knowledge questions (history, geography, science facts)
- Definitions or explanations
- Casual conversation
- Questions you can answer directly

REQUIRED TOOL CALL FORMAT (DO NOT CHANGE):
<tool_call>
{
    "tool_name": "calculator",
    "parameters": {
        "expression": "your_expression_here"
    }
}
</tool_call>

Examples:
- "What's 15 + 27?" -> Use calculator tool
- "What's the area of a circle with radius 5?" -> Use calculator tool  
- "What's the weather like?" -> Use weather_checker tool
- "Temperature in Paris" -> Use weather_checker tool
- "Schedule a meeting tomorrow" -> Use calendar_scheduler tool
- "What is the capital of France?" -> Respond normally, no tool needed
- "How are you today?" -> Respond normally, no tool needed

GENERAL TOOL GUIDELINES:
- Use tools when the request requires computation, external data, or specific functionality
- For calculator: Use mathematical expressions, not natural language
- For calculator: KEEP units like "degrees" in the expression (e.g., "sin(59 degrees)")
- For weather: Provide location if available
- For calendar: Include date/time details when scheduling
- Always use "evaluate" mode for calculator unless specifically solving equations
"""
        
        return prompt
    
    def parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse tool call from LLM response - handles only the first tool call if multiple exist"""
        # Look for tool call pattern - handle various formats
        patterns = [
            # Complete tool call
            r'<tool_call>\s*(.*?)\s*</tool_call>',
            # Incomplete tool call (missing closing tag)
            r'<tool_call>\s*(\{.*?\})\s*(?:\n|$)',
            # Even more flexible - just look for JSON after <tool_call>
            r'<tool_call>\s*(\{[^<]*?\})',
        ]
        
        tool_call_json = None
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                tool_call_json = match.group(1).strip()
                print(f"[DEBUG] Found tool call JSON with pattern: {tool_call_json}")
                break
        
        # If no wrapped tool call found, check for bare JSON tool call
        if not tool_call_json:
            # Look for bare JSON that looks like a tool call
            bare_json_pattern = r'^\s*(\{"tool_name":\s*"[^"]+",\s*"parameters":\s*\{[^}]*\}\})\s*$'
            match = re.search(bare_json_pattern, response.strip(), re.MULTILINE)
            if match:
                tool_call_json = match.group(1).strip()
                print(f"[DEBUG] Found bare JSON tool call: {tool_call_json}")
        
        if not tool_call_json:
            print(f"[DEBUG] No tool call pattern found in response: {repr(response[:200])}")
            return None
        
        # Handle case where multiple tool calls might be concatenated
        # Split on common delimiters and take the first valid JSON
        possible_jsons = [
            tool_call_json,
            tool_call_json.split(' 和 ')[0],  # Handle Chinese "and" 
            tool_call_json.split(' and ')[0],  # Handle English "and"
            tool_call_json.split('\n')[0],     # Handle newline separation
        ]
        
        for json_candidate in possible_jsons:
            json_candidate = json_candidate.strip()
            if json_candidate.startswith('{') and json_candidate.endswith('}'):
                try:
                    tool_call = json.loads(json_candidate)
                    
                    # Check if this is a malformed calculator call (missing tool_name and parameters wrapper)
                    if "expression" in tool_call and "tool_name" not in tool_call:
                        print(f"[DEBUG] Detected malformed calculator call, fixing...")
                        # Fix the structure
                        fixed_tool_call = {
                            "tool_name": "calculator",
                            "parameters": tool_call
                        }
                        print(f"[DEBUG] Fixed tool call: {fixed_tool_call}")
                        return fixed_tool_call
                    
                    # Validate tool call structure
                    if "tool_name" not in tool_call or "parameters" not in tool_call:
                        continue
                    
                    print(f"[DEBUG] Successfully parsed tool call: {tool_call}")
                    return tool_call
                except json.JSONDecodeError as e:
                    print(f"[DEBUG] JSON decode error for candidate '{json_candidate[:50]}...': {e}")
                    continue
        
        print(f"[DEBUG] All JSON parsing attempts failed")
        return {"error": "Could not parse any valid tool call JSON"}
    
    def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return results"""
        if "error" in tool_call:
            return tool_call
        
        tool_name = tool_call.get("tool_name")
        parameters = tool_call.get("parameters", {})
        
        print(f"[DEBUG] Executing tool: {tool_name} with parameters: {parameters}")
        
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
            
            print(f"[DEBUG] Tool execution result: {result}")
            
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result,
                "success": "error" not in result
            }
            
        except Exception as e:
            print(f"[DEBUG] Tool execution failed with exception: {e}")
            return {
                "tool_name": tool_name,
                "parameters": parameters,
                "error": f"Tool execution error: {str(e)}",
                "success": False
            }
    
    def process_response_with_tools(self, llm_response: str) -> Dict[str, Any]:
        """Process LLM response, execute any tool calls, and return formatted result"""
        print(f"[DEBUG] Processing LLM response for tool calls")
        
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
        
        # Remove ALL tool call patterns from response text to make it speech-ready
        cleaned_response = llm_response
        
        # Remove complete tool calls
        cleaned_response = re.sub(r'<tool_call>.*?</tool_call>', '', cleaned_response, flags=re.DOTALL)
        
        # Remove incomplete tool calls
        cleaned_response = re.sub(r'<tool_call>\s*\{[^<]*?\}\s*(?:\n|$)', '', cleaned_response, flags=re.DOTALL)
        
        # Remove any remaining <tool_call> tags
        cleaned_response = re.sub(r'</?tool_call[^>]*>', '', cleaned_response)
        
        # Clean up extra whitespace and newlines
        cleaned_response = re.sub(r'\n\s*\n', '\n', cleaned_response)
        cleaned_response = cleaned_response.strip()
        
        print(f"[DEBUG] Cleaned response: '{cleaned_response}'")
        
        return {
            "type": "tool_response",
            "content": cleaned_response,
            "tool_used": True,
            "tool_call": tool_call,
            "tool_result": tool_result
        }
    
    def format_tool_result_for_user(self, tool_result: Dict[str, Any]) -> str:
        """Format tool execution result for user display"""
        # Check if there's an error in the tool result
        if "error" in tool_result.get("result", {}):
            return f"❌ {tool_result['result']['error']}"
        
        # Check if the tool execution itself failed
        if not tool_result.get("success", False):
            error_msg = tool_result.get("error", "Unknown error")
            return f"❌ Tool Error: {error_msg}"
        
        tool_name = tool_result.get("tool_name", "unknown")
        result = tool_result.get("result", {})
        
        if tool_name == "calculator":
            if "calculation" in result:
                return f"🧮 **{result['calculation']}**"
            elif "formatted_result" in result:
                return f"🧮 **Result: {result['formatted_result']}**"
            elif "result" in result:
                return f"🧮 **Result: {result['result']}**"
            else:
                return f"🧮 **Calculation completed**"
        
        elif tool_name == "weather_checker":
            if "summary" in result:
                return f"🌤️ {result['summary']}"
        
        elif tool_name == "calendar_scheduler":
            if "message" in result:
                return f"📅 {result['message']}"
        
        # Fallback: return raw result
        return f"🔧 {tool_name}: {json.dumps(result, indent=2)}" 