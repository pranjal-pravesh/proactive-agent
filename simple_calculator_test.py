#!/usr/bin/env python3
"""
Simple test to check calculator imports
"""

try:
    import sympy as sp
    print("✅ Sympy is installed and working")
    
    # Test a simple calculation
    result = sp.factorial(7) / (sp.factorial(2) * sp.factorial(3))
    print(f"✅ Simple test: 7! / (2! * 3!) = {result}")
    
except ImportError:
    print("❌ Sympy is not installed. Install with: pip install sympy")
    exit(1)

try:
    import sys
    sys.path.append('src')
    from tool_calls.calculator import Calculator
    print("✅ Calculator imports successfully")
    
    # Test a simple calculation
    result = Calculator.execute("7! / (2! * 3!)")
    if "error" in result:
        print(f"❌ Calculator error: {result['error']}")
    else:
        print(f"✅ Calculator test: {result['calculation']}")
        
except Exception as e:
    print(f"❌ Error importing calculator: {e}") 