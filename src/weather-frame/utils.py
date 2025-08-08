import json
import os

def load_weather_icons():
    """Load weather icons mapping from JSON file"""
    with open(os.path.join(os.path.dirname(__file__), 'weather_icons.json'), 'r') as f:
        return json.load(f)

def get_weather_icon(weather_code, icons_mapping):
    """Get weather icon filename for a given weather code"""
    return icons_mapping.get(str(weather_code), "default.png")