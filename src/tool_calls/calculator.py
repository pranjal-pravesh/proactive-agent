import math
import json
import re
from typing import Dict, Any
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

class Calculator:
    """Enhanced calculator tool for complex mathematical operations"""
    
    @staticmethod
    def get_tool_info() -> Dict[str, Any]:
        """Get tool information for LLM"""
        return {
            "name": "calculator",
            "description": "Perform mathematical calculations using mathematical expressions and formulas. IMPORTANT: Only use mathematical notation, NOT natural language descriptions. Examples: '2*pi*r' not 'perimeter of circle', 'pi*r^2' not 'area of circle', '7!' not 'factorial of 7'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression using proper mathematical notation. Use: +, -, *, /, ^, sqrt(), sin(), cos(), tan(), log(), pi, e, factorial(). Examples: '2*pi*7' (perimeter), 'pi*7^2' (area), '7!/2!' (factorial division), 'sqrt(144)', 'sin(pi/2)', etc. DO NOT use natural language like 'perimeter of circle' - use the actual formula like '2*pi*r'."
                    },
                    "mode": {
                        "type": "string",
                        "description": "Calculation mode",
                        "enum": ["evaluate", "simplify", "expand", "factor", "solve", "integrate", "differentiate", "limit"],
                        "default": "evaluate"
                    },
                    "variable": {
                        "type": "string",
                        "description": "Variable for calculus operations (default: x)",
                        "default": "x"
                    }
                },
                "required": ["expression"]
            }
        }
    
    @staticmethod
    def _preprocess_expression(expr_str: str) -> str:
        """Preprocess expression to handle common mathematical notation"""
        # Handle factorial notation
        expr_str = re.sub(r'(\d+)!', r'factorial(\1)', expr_str)
        expr_str = re.sub(r'(\w+)!', r'factorial(\1)', expr_str)
        
        # Handle common function names
        replacements = {
            'ln': 'log',  # natural log in sympy is just log
            'lg': 'log10',  # log base 10
            'arcsin': 'asin',
            'arccos': 'acos',
            'arctan': 'atan',
            'deg': 'pi/180*',  # convert degrees to radians
        }
        
        for old, new in replacements.items():
            expr_str = re.sub(r'\b' + old + r'\b', new, expr_str)
        
        # Handle implicit multiplication for common cases
        # Like 2x -> 2*x, 3(x+1) -> 3*(x+1)
        expr_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr_str)
        expr_str = re.sub(r'(\d)\(', r'\1*(', expr_str)
        expr_str = re.sub(r'\)(\d)', r')*\1', expr_str)
        expr_str = re.sub(r'\)([a-zA-Z])', r')*\1', expr_str)
        
        return expr_str
    
    @staticmethod
    def _safe_evaluate(expr, timeout=30):
        """Safely evaluate expression with timeout"""
        try:
            # Use sympy's numerical evaluation
            result = float(expr.evalf())
            return result
        except Exception as e:
            # If numerical evaluation fails, try to simplify and then evaluate
            try:
                simplified = sp.simplify(expr)
                result = float(simplified.evalf())
                return result
            except:
                # Return symbolic result if numerical evaluation impossible
                return expr
    
    @staticmethod
    def execute(expression: str, mode: str = "evaluate", variable: str = "x") -> Dict[str, Any]:
        """Execute calculator operation"""
        try:
            # Preprocess the expression
            preprocessed_expr = Calculator._preprocess_expression(expression.strip())
            
            # Parse the expression using sympy
            transformations = standard_transformations + (implicit_multiplication_application,)
            
            try:
                # Parse expression
                parsed_expr = parse_expr(preprocessed_expr, transformations=transformations)
            except Exception as e:
                # Fallback: try with basic parsing
                try:
                    parsed_expr = sp.sympify(preprocessed_expr)
                except Exception as e2:
                    error_msg = str(e2).lower()
                    if any(word in error_msg for word in ['perimeter', 'area', 'circumference', 'volume']):
                        return {"error": f"Please use mathematical formulas instead of natural language. For example: 'perimeter of circle' → '2*pi*r', 'area of circle' → 'pi*r^2', 'area of rectangle' → 'length*width'"}
                    else:
                        return {"error": f"Could not parse expression '{expression}': {str(e2)}. Please use mathematical notation like '2*pi*5' instead of 'perimeter of circle with radius 5'."}
            
            # Handle different modes
            if mode == "evaluate":
                result = Calculator._safe_evaluate(parsed_expr)
                
                # Format result appropriately
                if isinstance(result, (int, float)):
                    if result == int(result):
                        formatted_result = str(int(result))
                    else:
                        formatted_result = f"{result:.10g}"  # Remove trailing zeros
                else:
                    formatted_result = str(result)
                
                return {
                    "result": result,
                    "formatted_result": formatted_result,
                    "calculation": f"{expression} = {formatted_result}",
                    "original_expression": expression,
                    "parsed_expression": str(parsed_expr)
                }
            
            elif mode == "simplify":
                simplified = sp.simplify(parsed_expr)
                return {
                    "result": simplified,
                    "formatted_result": str(simplified),
                    "calculation": f"Simplified: {expression} = {simplified}",
                    "original_expression": expression
                }
            
            elif mode == "expand":
                expanded = sp.expand(parsed_expr)
                return {
                    "result": expanded,
                    "formatted_result": str(expanded),
                    "calculation": f"Expanded: {expression} = {expanded}",
                    "original_expression": expression
                }
            
            elif mode == "factor":
                factored = sp.factor(parsed_expr)
                return {
                    "result": factored,
                    "formatted_result": str(factored),
                    "calculation": f"Factored: {expression} = {factored}",
                    "original_expression": expression
                }
            
            elif mode == "solve":
                var = sp.Symbol(variable)
                solutions = sp.solve(parsed_expr, var)
                solutions_str = [str(sol) for sol in solutions]
                return {
                    "result": solutions,
                    "formatted_result": ", ".join(solutions_str) if solutions_str else "No solutions",
                    "calculation": f"Solutions for {expression} = 0: {', '.join(solutions_str) if solutions_str else 'No solutions'}",
                    "original_expression": expression,
                    "variable": variable
                }
            
            elif mode == "integrate":
                var = sp.Symbol(variable)
                try:
                    integral = sp.integrate(parsed_expr, var)
                    return {
                        "result": integral,
                        "formatted_result": str(integral) + " + C",
                        "calculation": f"∫({expression}) d{variable} = {integral} + C",
                        "original_expression": expression,
                        "variable": variable
                    }
                except Exception as e:
                    return {"error": f"Could not integrate expression: {str(e)}"}
            
            elif mode == "differentiate":
                var = sp.Symbol(variable)
                try:
                    derivative = sp.diff(parsed_expr, var)
                    return {
                        "result": derivative,
                        "formatted_result": str(derivative),
                        "calculation": f"d/d{variable}({expression}) = {derivative}",
                        "original_expression": expression,
                        "variable": variable
                    }
                except Exception as e:
                    return {"error": f"Could not differentiate expression: {str(e)}"}
            
            elif mode == "limit":
                var = sp.Symbol(variable)
                try:
                    # For limit, we need to specify approach point
                    # Default to 0 if not specified in expression
                    limit_result = sp.limit(parsed_expr, var, 0)
                    return {
                        "result": limit_result,
                        "formatted_result": str(limit_result),
                        "calculation": f"lim({variable}→0) {expression} = {limit_result}",
                        "original_expression": expression,
                        "variable": variable
                    }
                except Exception as e:
                    return {"error": f"Could not compute limit: {str(e)}"}
            
            else:
                return {"error": f"Unknown mode: {mode}"}
                
        except Exception as e:
            return {"error": f"Calculation error: {str(e)}"}
    
    @staticmethod
    def test_complex_calculations():
        """Test method for complex calculations"""
        test_cases = [
            "7! / (2! * 3!)",
            "sin(pi/2)",
            "log(e^3)",
            "sqrt(144) + 2^3",
            "factorial(5) * factorial(3)",
            "integrate(x^2, x)",
            "diff(x^3 + 2*x^2 + x, x)",
            "solve(x^2 - 4, x)",
            "simplify((x^2 - 1)/(x - 1))"
        ]
        
        results = {}
        for expr in test_cases:
            result = Calculator.execute(expr)
            results[expr] = result
        
        return results 