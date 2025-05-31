import json
import requests
from typing import Dict, Any
from datetime import datetime
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # python-dotenv not installed, skip loading

class WeatherChecker:
    """Weather checking tool using weatherstack API"""
    
    # Weatherstack API configuration
    BASE_URL = "http://api.weatherstack.com"
    HTTPS_URL = "https://api.weatherstack.com"  # For paid plans
    
    @staticmethod
    def get_tool_info() -> Dict[str, Any]:
        """Get tool information for LLM"""
        return {
            "name": "weather_checker",
            "description": "Get current weather information for specified locations. Only use this when the user specifically asks about weather, temperature, or weather conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, region, or location (e.g., 'New York', 'London, UK', 'Tokyo, Japan', 'latitude,longitude')"
                    },
                    "units": {
                        "type": "string",
                        "description": "Temperature units: 'm' for metric (Celsius), 'f' for Fahrenheit, 's' for scientific",
                        "enum": ["m", "f", "s"],
                        "default": "m"
                    }
                },
                "required": ["location"]
            }
        }
    
    @staticmethod
    def _get_api_key():
        """Get weatherstack API key from environment variable or config"""
        # Try environment variable first
        api_key = os.getenv('WEATHERSTACK_API_KEY')
        if api_key:
            return api_key
        
        # Try reading from config file
        try:
            import yaml
            with open('configs/config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                return config.get('weatherstack', {}).get('api_key')
        except:
            pass
        
        # Return None if no API key found
        return None
    
    @staticmethod
    def _handle_api_error(error_code: int, error_type: str, error_info: str) -> str:
        """Handle weatherstack API errors with user-friendly messages"""
        error_messages = {
            101: "Weather service authentication failed. Please check API key configuration.",
            104: "Monthly API request limit reached. Please upgrade the weather service plan.",
            601: f"Invalid location '{error_info}'. Please provide a valid city name or coordinates.",
            615: "Weather service request failed. Please try again later.",
            404: "Weather data not found for the requested location.",
            429: "Too many weather requests. Please wait a moment and try again.",
            403: "Weather service feature not available on current plan."
        }
        
        return error_messages.get(error_code, f"Weather service error: {error_info}")
    
    @staticmethod
    def execute(location: str, units: str = "m") -> Dict[str, Any]:
        """Execute weather checking operation using weatherstack API"""
        try:
            # Get API key
            api_key = WeatherChecker._get_api_key()
            if not api_key:
                return {
                    "error": "Weather service not configured. Please run 'python setup_weather.py' to set up your API key, or set the WEATHERSTACK_API_KEY environment variable."
                }
            
            # Prepare API request
            url = f"{WeatherChecker.BASE_URL}/current"
            params = {
                "access_key": api_key,
                "query": location,
                "units": units
            }
            
            # Make API request with timeout
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Check for API errors
            if not data.get("success", True) and "error" in data:
                error = data["error"]
                error_message = WeatherChecker._handle_api_error(
                    error.get("code", 0),
                    error.get("type", "unknown"),
                    error.get("info", "Unknown error")
                )
                return {"error": error_message}
            
            # Check if we have valid weather data
            if "current" not in data or "location" not in data:
                return {"error": f"No weather data available for '{location}'. Please check the location name."}
            
            # Extract weather information
            current = data["current"]
            location_info = data["location"]
            
            # Determine temperature unit symbol
            unit_symbol = {
                "m": "°C",
                "f": "°F", 
                "s": "K"
            }.get(units, "°C")
            
            # Format weather response
            weather_data = {
                "location": f"{location_info.get('name', location)}, {location_info.get('country', '')}".strip(", "),
                "region": location_info.get("region", ""),
                "temperature": current.get("temperature"),
                "feels_like": current.get("feelslike"),
                "condition": current.get("weather_descriptions", ["Unknown"])[0],
                "humidity": current.get("humidity"),
                "wind_speed": current.get("wind_speed"),
                "wind_direction": current.get("wind_dir"),
                "pressure": current.get("pressure"),
                "visibility": current.get("visibility"),
                "uv_index": current.get("uv_index"),
                "local_time": location_info.get("localtime"),
                "units": units,
                "unit_symbol": unit_symbol
            }
            
            # Create summary message
            summary_parts = [
                f"Weather in {weather_data['location']}:",
                f"{weather_data['temperature']}{unit_symbol}",
                f"{weather_data['condition']}"
            ]
            
            if weather_data.get('feels_like') and weather_data['feels_like'] != weather_data['temperature']:
                summary_parts.append(f"(feels like {weather_data['feels_like']}{unit_symbol})")
            
            if weather_data.get('humidity'):
                summary_parts.append(f"Humidity: {weather_data['humidity']}%")
            
            if weather_data.get('wind_speed'):
                wind_text = f"Wind: {weather_data['wind_speed']} km/h"
                if weather_data.get('wind_direction'):
                    wind_text += f" {weather_data['wind_direction']}"
                summary_parts.append(wind_text)
            
            summary = ", ".join(summary_parts)
            
            return {
                "location": weather_data['location'],
                "data": weather_data,
                "summary": summary,
                "success": True
            }
            
        except requests.RequestException as e:
            return {"error": f"Weather service connection failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "Weather service returned invalid data. Please try again."}
        except Exception as e:
            return {"error": f"Weather service error: {str(e)}"} 