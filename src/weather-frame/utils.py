from config import WEATHER_ICONS

def get_weather_icon(weather_code):
    """Get weather icon filename for a given weather code"""
    return WEATHER_ICONS.get(str(weather_code), "default.png")