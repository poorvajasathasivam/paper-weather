# app/tests/test_weather_api.py
import pytest
from unittest.mock import patch, MagicMock
from ..utils.weather_api import WeatherAPI, get_weather

@pytest.fixture
def mock_weather_data():
    return {
        "name": "London",
        "sys": {"country": "GB"},
        "main": {
            "temp": 15.2,
            "feels_like": 14.5,
            "humidity": 76
        },
        "weather": [{"description": "cloudy"}],
        "wind": {"speed": 5.1}
    }

def test_format_weather_data(mock_weather_data):
    """Test weather data formatting."""
    formatted = WeatherAPI.format_weather_data(mock_weather_data)
    
    assert "London" in formatted
    assert "GB" in formatted
    assert "15.2°C" in formatted
    assert "14.5°C" in formatted
    assert "cloudy" in formatted
    assert "76%" in formatted
    assert "5.1 m/s" in formatted

@patch('requests.get')
def test_get_weather_by_city(mock_get, mock_weather_data):
    """Test weather API call."""
    # Configure the mock
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = mock_weather_data
    mock_get.return_value = mock_response
    
    # Call the function
    result = WeatherAPI.get_weather_by_city("London")
    
    # Verify the result
    assert result == mock_weather_data
    mock_get.assert_called_once()
    assert "London" in mock_get.call_args[1]["params"]["q"]

@patch('app.utils.weather_api.WeatherAPI.get_weather_by_city')
def test_get_weather(mock_get_weather, mock_weather_data):
    """Test the convenience function."""
    # Configure the mock
    mock_get_weather.return_value = mock_weather_data
    
    # Call the function
    result = get_weather("London")
    
    # Verify the result
    assert "London" in result
    assert "15.2°C" in result
    mock_get_weather.assert_called_once_with("London")

@patch('app.utils.weather_api.WeatherAPI.get_weather_by_city')
def test_get_weather_error(mock_get_weather):
    """Test error handling."""
    # Configure the mock to raise an exception
    mock_get_weather.side_effect = Exception("API error")
    
    # Call the function
    result = get_weather("NonexistentCity")
    
    # Verify the result contains an error message
    assert "Error" in result
    assert "API error" in result