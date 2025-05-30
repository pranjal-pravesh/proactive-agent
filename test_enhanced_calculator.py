#!/usr/bin/env python3
"""
Test script for the enhanced calculator functionality
"""

import sys
sys.path.append('src')

from tool_calls.calculator import Calculator

def test_calculator():
    """Test the enhanced calculator with various complex expressions"""
    
    print("=== Enhanced Calculator Test ===\n")
    
    # Test cases from the user's requirements and more
    test_cases = [
        # Basic factorial expressions
        ("7! / (2! * 3!)", "evaluate"),
        ("factorial(7) / (factorial(2) * factorial(3))", "evaluate"),
        
        # Complex arithmetic
        ("sqrt(144) + 2^3", "evaluate"),
        ("sin(pi/2) + cos(0)", "evaluate"),
        ("log(e^3)", "evaluate"),
        ("ln(e^2)", "evaluate"),
        
        # Higher complexity calculations
        ("(10! / 5!) / (8! / 3!)", "evaluate"),
        ("sin(pi/3) * cos(pi/6) + tan(pi/4)", "evaluate"),
        ("sqrt(factorial(5)) + log10(1000)", "evaluate"),
        
        # Symbolic math
        ("(x^2 - 1)/(x - 1)", "simplify"),
        ("(x + 1)^3", "expand"),
        ("x^3 - 1", "factor"),
        
        # Calculus
        ("x^3 + 2*x^2 + x", "differentiate"),
        ("x^2", "integrate"),
        ("x^2 - 4", "solve"),
        
        # Very complex expressions
        ("factorial(8) / (factorial(3) * factorial(5)) + sin(pi/2)^2", "evaluate"),
        ("sqrt(factorial(6)) + log(e^5) - cos(0)", "evaluate"),
    ]
    
    for expression, mode in test_cases:
        print(f"Testing: {expression} (mode: {mode})")
        result = Calculator.execute(expression, mode)
        
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  ✅ Result: {result.get('calculation', result.get('formatted_result', str(result.get('result'))))}")
        print()

if __name__ == "__main__":
    try:
        test_calculator()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure sympy is installed: pip install sympy")
    except Exception as e:
        print(f"Error: {e}") 