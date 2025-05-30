import json
import random
from typing import Dict, Any
from datetime import datetime

class WeatherChecker:
    """Weather checking tool (placeholder implementation)"""
    
    @staticmethod
    def get_tool_info() -> Dict[str, Any]:
        """Get tool information for LLM"""
        return {
            "name": "weather_checker",
            "description": "Get current weather information and forecasts for specified locations",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or location (e.g., 'New York', 'London', 'Tokyo')"
                    },
                    "action": {
                        "type": "string",
                        "description": "Type of weather information to get",
                        "enum": ["current", "forecast", "hourly"]
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days for forecast (1-7, default: 3)",
                        "minimum": 1,
                        "maximum": 7
                    }
                },
                "required": ["location", "action"]
            }
        }
    
    @staticmethod
    def execute(location: str, action: str = "current", days: int = 3) -> Dict[str, Any]:
        """Execute weather checking operation (placeholder)"""
        try:
            # Simulate API delay
            import time
            time.sleep(0.1)
            
            # Mock weather conditions
            conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "thunderstorm", "snow", "fog"]
            temperatures = list(range(-10, 40))  # -10°C to 40°C
            humidity_levels = list(range(20, 100))
            wind_speeds = list(range(0, 30))
            
            if action == "current":
                current_weather = {
                    "location": location,
                    "temperature": random.choice(temperatures),
                    "condition": random.choice(conditions),
                    "humidity": random.choice(humidity_levels),
                    "wind_speed": random.choice(wind_speeds),
                    "timestamp": datetime.now().isoformat(),
                    "feels_like": random.choice(temperatures)
                }
                
                return {
                    "action": "current",
                    "data": current_weather,
                    "summary": f"Current weather in {location}: {current_weather['temperature']}°C, {current_weather['condition']}, humidity {current_weather['humidity']}%, wind {current_weather['wind_speed']} km/h"
                }
            
            elif action == "forecast":
                days = max(1, min(7, days))  # Ensure days is between 1 and 7
                forecast_data = []
                
                for i in range(days):
                    day_forecast = {
                        "day": i + 1,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "high_temp": random.choice(temperatures),
                        "low_temp": random.choice([t for t in temperatures if t < 20]),
                        "condition": random.choice(conditions),
                        "precipitation_chance": random.randint(0, 100)
                    }
                    forecast_data.append(day_forecast)
                
                return {
                    "action": "forecast",
                    "location": location,
                    "days": days,
                    "data": forecast_data,
                    "summary": f"{days}-day forecast for {location} ready"
                }
            
            elif action == "hourly":
                hourly_data = []
                for hour in range(24):
                    hour_forecast = {
                        "hour": f"{hour:02d}:00",
                        "temperature": random.choice(temperatures),
                        "condition": random.choice(conditions),
                        "precipitation_chance": random.randint(0, 100)
                    }
                    hourly_data.append(hour_forecast)
                
                return {
                    "action": "hourly",
                    "location": location,
                    "data": hourly_data,
                    "summary": f"24-hour forecast for {location} ready"
                }
            
            else:
                return {"error": f"Unknown weather action: {action}"}
                
        except Exception as e:
            return {"error": f"Weather service error: {str(e)}"} 