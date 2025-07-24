from datetime import datetime
import locale
import requests

from flask import Flask, render_template
from geopy.geocoders import Nominatim

from config import API_URL, PARAMS

app = Flask(__name__)

def fetch_weather(api_url=API_URL, params=PARAMS):
    r = requests.get(api_url, params=params)
    r.raise_for_status()
    return r.json()

def get_location(lat, long):
    try:
        geolocator = Nominatim(user_agent="weather-frame", timeout=10)
        location = geolocator.reverse(f"{lat}, {long}", language='nl')
        
        if location:
            # Return just the city/town name if available, otherwise the full address
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

@app.route("/")
def dashboard():
    # Set Dutch locale
    try:
        locale.setlocale(locale.LC_TIME, 'nl_NL')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'nl_NL.UTF-8')
        except locale.Error:
            print("Dutch locale not available, falling back to default")
    
    data = fetch_weather()
    
    current = data['current']
    current_time = datetime.fromisoformat(current['time'])
    current['formatted_date'] = current_time.strftime('%A %d %B').capitalize()
    
    hourly = data['hourly']
    current_hour_index = 0

    for i, time_str in enumerate(hourly['time']):
        hourly_time = datetime.fromisoformat(time_str)
        if hourly_time.hour == current_time.hour and hourly_time.date() == current_time.date():
            current_hour_index = i
            break
    daily = data['daily']

    for i, day in enumerate(daily['time']):
        daily_time = datetime.fromisoformat(day)
        weekday = daily_time.strftime('%A')  # Full English day name
        daily['time'][i] = weekday[:2]

    return render_template(
        "index.html", 
        current=current, 
        hourly=hourly,
        current_hour_index=current_hour_index,
        daily=daily, 
        location=get_location(data['latitude'], data['longitude'])
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)