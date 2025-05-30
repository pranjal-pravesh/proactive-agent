import math
import json
from typing import Dict, Any

class Calculator:
    """Calculator tool for mathematical operations"""
    
    @staticmethod
    def get_tool_info() -> Dict[str, Any]:
        """Get tool information for LLM"""
        return {
            "name": "calculator",
            "description": "Perform mathematical calculations including basic arithmetic, trigonometry, and advanced functions",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "The mathematical operation to perform",
                        "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt", "sin", "cos", "tan", "log", "ln", "factorial", "evaluate"]
                    },
                    "a": {
                        "type": "number",
                        "description": "First number (required for most operations)"
                    },
                    "b": {
                        "type": "number", 
                        "description": "Second number (required for binary operations)"
                    },
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (for 'evaluate' operation)"
                    }
                },
                "required": ["operation"]
            }
        }
    
    @staticmethod
    def execute(operation: str, a: float = None, b: float = None, expression: str = None) -> Dict[str, Any]:
        """Execute calculator operation"""
        try:
            if operation == "add":
                if a is None or b is None:
                    return {"error": "Addition requires two numbers (a and b)"}
                result = a + b
                return {"result": result, "calculation": f"{a} + {b} = {result}"}
            
            elif operation == "subtract":
                if a is None or b is None:
                    return {"error": "Subtraction requires two numbers (a and b)"}
                result = a - b
                return {"result": result, "calculation": f"{a} - {b} = {result}"}
            
            elif operation == "multiply":
                if a is None or b is None:
                    return {"error": "Multiplication requires two numbers (a and b)"}
                result = a * b
                return {"result": result, "calculation": f"{a} × {b} = {result}"}
            
            elif operation == "divide":
                if a is None or b is None:
                    return {"error": "Division requires two numbers (a and b)"}
                if b == 0:
                    return {"error": "Cannot divide by zero"}
                result = a / b
                return {"result": result, "calculation": f"{a} ÷ {b} = {result}"}
            
            elif operation == "power":
                if a is None or b is None:
                    return {"error": "Power operation requires two numbers (a and b)"}
                result = a ** b
                return {"result": result, "calculation": f"{a}^{b} = {result}"}
            
            elif operation == "sqrt":
                if a is None:
                    return {"error": "Square root requires one number (a)"}
                if a < 0:
                    return {"error": "Cannot calculate square root of negative number"}
                result = math.sqrt(a)
                return {"result": result, "calculation": f"√{a} = {result}"}
            
            elif operation == "sin":
                if a is None:
                    return {"error": "Sine requires one number (a) in radians"}
                result = math.sin(a)
                return {"result": result, "calculation": f"sin({a}) = {result}"}
            
            elif operation == "cos":
                if a is None:
                    return {"error": "Cosine requires one number (a) in radians"}
                result = math.cos(a)
                return {"result": result, "calculation": f"cos({a}) = {result}"}
            
            elif operation == "tan":
                if a is None:
                    return {"error": "Tangent requires one number (a) in radians"}
                result = math.tan(a)
                return {"result": result, "calculation": f"tan({a}) = {result}"}
            
            elif operation == "log":
                if a is None:
                    return {"error": "Logarithm requires one number (a)"}
                if a <= 0:
                    return {"error": "Logarithm requires positive number"}
                result = math.log10(a)
                return {"result": result, "calculation": f"log₁₀({a}) = {result}"}
            
            elif operation == "ln":
                if a is None:
                    return {"error": "Natural logarithm requires one number (a)"}
                if a <= 0:
                    return {"error": "Natural logarithm requires positive number"}
                result = math.log(a)
                return {"result": result, "calculation": f"ln({a}) = {result}"}
            
            elif operation == "factorial":
                if a is None:
                    return {"error": "Factorial requires one number (a)"}
                if a < 0 or a != int(a):
                    return {"error": "Factorial requires non-negative integer"}
                result = math.factorial(int(a))
                return {"result": result, "calculation": f"{int(a)}! = {result}"}
            
            elif operation == "evaluate":
                if expression is None:
                    return {"error": "Evaluate operation requires an expression"}
                # Safe evaluation of mathematical expressions
                allowed_names = {
                    k: v for k, v in math.__dict__.items() if not k.startswith("__")
                }
                allowed_names.update({"abs": abs, "round": round})
                
                try:
                    result = eval(expression, {"__builtins__": {}}, allowed_names)
                    return {"result": result, "calculation": f"{expression} = {result}"}
                except Exception as e:
                    return {"error": f"Invalid expression: {str(e)}"}
            
            else:
                return {"error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"} 