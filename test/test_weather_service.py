import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Path adjustment may be needed based on your project structure
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'weather-frame'))

from weather_frame.weather_service import WeatherService
from weather_frame.config.api_config import API_URL, PARAMS

@pytest.fixture
def weather_service():
    """Return a WeatherService instance for testing."""
    return WeatherService()

@pytest.fixture
def sample_weather_data():
    """Return sample weather data for testing."""
    return {
        "latitude": 52.16,
        "longitude": 4.49,
        "current": {
            "time": "2025-08-12T14:00",
            "temperature_2m": 21.5,
            "weathercode": 1
        },
        "hourly": {
            "time": [
                "2025-08-12T00:00", "2025-08-12T01:00", "2025-08-12T02:00", 
                "2025-08-12T03:00", "2025-08-12T04:00", "2025-08-12T05:00",
                "2025-08-12T06:00", "2025-08-12T07:00", "2025-08-12T08:00", 
                "2025-08-12T09:00", "2025-08-12T10:00", "2025-08-12T11:00",
                "2025-08-12T12:00", "2025-08-12T13:00", "2025-08-12T14:00", 
                "2025-08-12T15:00"
            ],
            "temperature_2m": [
                18.0, 17.5, 17.0, 16.5, 16.0, 16.5, 
                17.0, 18.0, 19.0, 20.0, 21.0, 21.5, 
                22.0, 22.0, 21.5, 21.0
            ],
            "weathercode": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
            "rain": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        "daily": {
            "time": [
                "2025-08-12", "2025-08-13", "2025-08-14",
                "2025-08-15", "2025-08-16", "2025-08-17", "2025-08-18"
            ],
            "temperature_2m_max": [22.0, 23.5, 24.0, 21.0, 20.5, 22.0, 23.0],
            "temperature_2m_min": [16.0, 17.0, 18.0, 15.0, 14.5, 16.0, 17.0],
            "weathercode": [1, 1, 2, 3, 80, 1, 0]
        }
    }

@patch('weather_service.requests.get')
def test_fetch_weather(mock_get, weather_service, sample_weather_data):
    """Test fetching weather data from API."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = sample_weather_data
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Call the method
    result = weather_service.fetch_weather()
    
    # Assertions
    assert result == sample_weather_data
    mock_get.assert_called_once_with(API_URL, params=PARAMS)

@patch('weather_service.Nominatim')
def test_get_location_city(mock_nominatim, weather_service):
    """Test getting location when city is available."""
    # Setup mock response
    mock_geolocator = MagicMock()
    mock_location = MagicMock()
    mock_location.raw = {'address': {'city': 'Leiden'}}
    mock_geolocator.reverse.return_value = mock_location
    mock_nominatim.return_value = mock_geolocator
    
    # Call the method
    result = weather_service.get_location(52.16, 4.49)
    
    # Assertions
    assert result == 'Leiden'
    mock_nominatim.assert_called_once_with(user_agent="weather-frame", timeout=10)
    mock_geolocator.reverse.assert_called_once_with("52.16, 4.49", language='nl')

@patch('weather_service.Nominatim')
def test_get_location_town(mock_nominatim, weather_service):
    """Test getting location when town is available but not city."""
    # Setup mock response
    mock_geolocator = MagicMock()
    mock_location = MagicMock()
    mock_location.raw = {'address': {'town': 'Oegstgeest'}}
    mock_geolocator.reverse.return_value = mock_location
    mock_nominatim.return_value = mock_geolocator
    
    # Call the method
    result = weather_service.get_location(52.18, 4.46)
    
    # Assertions
    assert result == 'Oegstgeest'

@patch('weather_service.Nominatim')
def test_get_location_exception(mock_nominatim, weather_service):
    """Test getting location when an exception occurs."""
    # Setup mock to raise exception
    mock_geolocator = MagicMock()
    mock_geolocator.reverse.side_effect = Exception("API Error")
    mock_nominatim.return_value = mock_geolocator
    
    # Call the method
    result = weather_service.get_location(52.16, 4.49)
    
    # Should return default
    assert result == 'Leiden'

def test_process_weather_data(weather_service, sample_weather_data):
    """Test processing weather data."""
    # Mock get_location to avoid external API call
    weather_service.get_location = MagicMock(return_value="Leiden")
    
    # Call the method
    result = weather_service.process_weather_data(sample_weather_data)
    
    # Assertions
    assert 'current' in result
    assert 'hourly' in result
    assert 'daily' in result
    assert 'location' in result
    assert 'last_updated' in result
    
    # Check time object creation
    assert result['current']['time_obj'] == datetime.fromisoformat("2025-08-12T14:00")
    
    # Check current hour index is set correctly (14:00 is index 14)
    assert result['current_hour_index'] == 14
    
    # Check daily time objects
    assert len(result['daily']['time_objects']) == 7
    assert result['daily']['time_objects'][0] == datetime.fromisoformat("2025-08-12")

@patch('weather_service.WeatherService.fetch_weather')
@patch('weather_service.WeatherService.process_weather_data')
def test_update_weather_data_success(mock_process, mock_fetch, weather_service, sample_weather_data):
    """Test updating weather data cache - successful case."""
    # Setup mocks
    mock_fetch.return_value = sample_weather_data
    processed_data = {'processed': True, 'data': sample_weather_data}
    mock_process.return_value = processed_data
    
    # Call the method
    result = weather_service.update_weather_data()
    
    # Assertions
    assert result is True
    mock_fetch.assert_called_once()
    mock_process.assert_called_once_with(sample_weather_data)
    assert weather_service.cache == processed_data

@patch('weather_service.WeatherService.fetch_weather')
def test_update_weather_data_failure(mock_fetch, weather_service):
    """Test updating weather data cache - failure case."""
    # Setup mock to raise exception
    mock_fetch.side_effect = Exception("API Error")
    
    # Call the method
    result = weather_service.update_weather_data()
    
    # Assertions
    assert result is False
    mock_fetch.assert_called_once()
    assert weather_service.cache == {}

def test_get_cached_data(weather_service):
    """Test getting cached weather data."""
    # Setup cache
    test_data = {'test': 'data'}
    weather_service.cache = test_data
    
    # Call the method
    result = weather_service.get_cached_data()
    
    # Assertions
    assert result == test_data
    assert result is weather_service.cache  # Reference check