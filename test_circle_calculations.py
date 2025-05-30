#!/usr/bin/env python3
"""
Test script to show correct circle calculations
"""

import sys
sys.path.append('src')

from tool_calls.calculator import Calculator

def test_circle_calculations():
    """Test proper circle perimeter and area calculations"""
    
    radius = 5
    print(f"Circle with radius {radius} cm:")
    print("=" * 30)
    
    # Calculate perimeter
    perimeter_result = Calculator.execute(f"2*pi*{radius}")
    if "error" not in perimeter_result:
        print(f"Perimeter: {perimeter_result['calculation']} cm")
    
    # Calculate area  
    area_result = Calculator.execute(f"pi*{radius}^2")
    if "error" not in area_result:
        print(f"Area: {area_result['calculation']} cm²")
    
    print("\nNote: These have different units and shouldn't be added together!")
    print(f"Perimeter = {perimeter_result.get('formatted_result', 'N/A')} cm (length)")
    print(f"Area = {area_result.get('formatted_result', 'N/A')} cm² (area)")

if __name__ == "__main__":
    test_circle_calculations() 