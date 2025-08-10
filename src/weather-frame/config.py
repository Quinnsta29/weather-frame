API_URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
    "latitude": 52.16,
    "longitude": 4.49,
    "current": "temperature_2m,weathercode",
    "hourly": "temperature_2m,weathercode,rain",
    "daily": "temperature_2m_max,temperature_2m_min,weathercode",
    "timezone": "auto"
}

WEATHER_ICONS = {
    "0": "clear.svg",
    "1": "partly_cloudy.svg",
    "2": "partly_cloudy.svg",
    "3": "partly_cloudy.svg",
    "45": "fog.svg",
    "48": "fog.svg",
    "51": "light_rain.svg",
    "53": "light_rain.svg",
    "55": "light_rain.svg",
    "56": "light_rain.svg",
    "57": "light_rain.svg",
    "61": "rain.svg",
    "63": "rain.svg",
    "65": "rain.svg",
    "66": "freezing_rain.svg",
    "67": "freezing_rain.svg",
    "71": "snow.svg",
    "73": "snow.svg",
    "75": "snow.svg",
    "77": "snow.svg",
    "80": "rain.svg",
    "81": "rain.svg",
    "82": "rain.svg",
    "85": "snow.svg",
    "86": "snow.svg",
    "95": "thunderstorm.svg",
    "96": "thunderstorm.svg",
    "99": "thunderstorm.svg"
}