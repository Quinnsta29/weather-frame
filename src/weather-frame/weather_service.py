import requests
from datetime import datetime
from geopy.geocoders import Nominatim
from config import API_URL, PARAMS

class WeatherService:
    def __init__(self):
        self.cache = {}
    
    def fetch_weather(self, api_url=API_URL, params=PARAMS):
        """Fetch weather data from API"""
        r = requests.get(api_url, params=params)
        r.raise_for_status()
        return r.json()
    
    def get_location(self, lat, long):
        """Get location name from coordinates"""
        try:
            geolocator = Nominatim(user_agent="weather-frame", timeout=10)
            location = geolocator.reverse(f"{lat}, {long}", language='nl')
            
            if location:
                address = location.raw['address']
                if 'city' in address:
                    return address['city']
                elif 'town' in address:
                    return address['town']
                elif 'village' in address:
                    return address['village']
                else:
                    return location.address.split(',')[0]
        except Exception as e:
            print(f"Error getting location: {e}")
            return "Leiden"
    
    def process_weather_data(self, data):
        """Process and format weather data"""
        current = data['current']
        current_time = datetime.fromisoformat(current['time'])
        current['time_obj'] = current_time
        # current['formatted_date'] = current_time.strftime('%A %d %B').capitalize()
        
        hourly = data['hourly']
        current_hour_index = 0

        for i, time_str in enumerate(hourly['time']):
            hourly_time = datetime.fromisoformat(time_str)
            if hourly_time.hour == current_time.hour and hourly_time.date() == current_time.date():
                current_hour_index = i
                break
        
        daily = data['daily']
        daily_times = []
        for i, day in enumerate(daily['time']):
            daily_time = datetime.fromisoformat(day)
            # weekday = daily_time.strftime('%A')
            # daily['time'][i] = weekday[:2]
            daily_times.append(daily_time)

        daily['time_objects'] = daily_times

        location = self.get_location(data['latitude'], data['longitude'])
        
        return {
            'current': current,
            'hourly': hourly,
            'current_hour_index': current_hour_index,
            'daily': daily,
            'location': location,
            'last_updated': datetime.now()
        }
    
    def update_weather_data(self):
        """Update weather data cache"""
        print(f"Updating weather data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            data = self.fetch_weather()
            self.cache = self.process_weather_data(data)
            return True
        except Exception as e:
            print(f"Error updating weather data: {e}")
            return False
    
    def get_cached_data(self):
        """Get cached weather data"""
        return self.cache