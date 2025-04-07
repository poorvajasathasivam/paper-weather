# app/utils/weather_api.py
import requests
from typing import Dict, Any, Optional

class WeatherAPI:
    """Utility class for fetching weather data from OpenWeatherMap API."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    @staticmethod
    def get_weather_by_city(city: str, api_key: str, units: str = "metric") -> Dict[str, Any]:
        """
        Fetch current weather data for a specific city.
        
        Args:
            city: The name of the city
            api_key: OpenWeatherMap API key
            units: Unit system (metric, imperial, standard)
            
        Returns:
            Dictionary containing weather data
        """
        params = {
            "q": city,
            "appid": api_key,
            "units": units
        }
        
        response = requests.get(WeatherAPI.BASE_URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        return response.json()
    
    @staticmethod
    def format_weather_data(weather_data: Dict[str, Any]) -> str:
        """
        Format raw weather data into a readable string.
        
        Args:
            weather_data: Raw weather data from API
            
        Returns:
            Formatted weather information string
        """
        city = weather_data.get("name", "Unknown")
        country = weather_data.get("sys", {}).get("country", "")
        temp = weather_data.get("main", {}).get("temp", "N/A")
        feels_like = weather_data.get("main", {}).get("feels_like", "N/A")
        description = weather_data.get("weather", [{}])[0].get("description", "N/A")
        humidity = weather_data.get("main", {}).get("humidity", "N/A")
        wind_speed = weather_data.get("wind", {}).get("speed", "N/A")
        
        return f"""
Current Weather in {city}, {country}:
- Temperature: {temp}°C
- Feels like: {feels_like}°C
- Conditions: {description}
- Humidity: {humidity}%
- Wind Speed: {wind_speed} m/s
"""

def get_weather(city: str, api_key: str) -> str:
    """
    Convenience function to get formatted weather for a city.
    
    Args:
        city: The name of the city
        api_key: OpenWeatherMap API key
        
    Returns:
        Formatted weather information string
    """
    try:
        weather_data = WeatherAPI.get_weather_by_city(city, api_key)
        return WeatherAPI.format_weather_data(weather_data)
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"