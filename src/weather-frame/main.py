import locale
import os
import requests
import subprocess
import time
from datetime import datetime
from threading import Thread

import atexit
from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from apscheduler.schedulers.background import BackgroundScheduler

from config import API_URL, PARAMS
from e_ink import display_screenshot

app = Flask(__name__)

# Global variable to store the current weather data
weather_cache = {}
screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
os.makedirs(screenshots_dir, exist_ok=True)
screenshot_path = os.path.join(screenshots_dir, 'screenshot.png')

def take_screenshot_and_update_display():
    """Take a screenshot of the weather dashoard using headless Chromium."""
    try:
        url = "http://localhost:80" # Adjust if needed
        cmd = [
            'chromium-browser',
            '--headless',
            '--disable-gpu',
            '--window-size=800,400',
            '--screenshot=' + screenshot_path,
            url
        ]
        subprocess.run(cmd, check=True)
        display_screenshot(screenshot_path)
        return True
    except Exception as e:
        # TODO: Do this as logging
        print(f"Error taking screenshot: {e}")
        return False
    
def update_weather_data():
    """Function to update the weather data cache"""
    global weather_cache
    print(f"Updating weather data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
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
            weekday = daily_time.strftime('%A')
            daily['time'][i] = weekday[:2]
        
        location = get_location(data['latitude'], data['longitude'])
        
        # Update the cache
        weather_cache.update({
            'current': current,
            'hourly': hourly,
            'current_hour_index': current_hour_index,
            'daily': daily,
            'location': location,
            'last_updated': datetime.now()
        })
        
        # Wait a bit for the web page to update with new data
        time.sleep(2)
        
        # Take a screenshot in a separate thread to avoid blocking
        Thread(target=take_screenshot_and_update_display).start()
        
        return True
    except Exception as e:
        print(f"Error updating weather data: {e}")
        return False

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
    
    # Use cached data if available, otherwise fetch it
    if not weather_cache:
        update_weather_data()
    
    return render_template(
        "index.html", 
        current=weather_cache['current'],
        hourly=weather_cache['hourly'],
        current_hour_index=weather_cache['current_hour_index'],
        daily=weather_cache['daily'],
        location=weather_cache['location'],
        last_updated=weather_cache['last_updated']
    )

@app.route("/refresh")
def refresh():
    """Manual refresh endpoint"""
    update_weather_data()
    return "Weather data refreshed"

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_weather_data, trigger="interval", hours=1)
scheduler.start()

# Add a lightweight client-side refresh
@app.after_request
def add_refresh_header(response):
    """Add auto-refresh header to index page"""
    if request.path == "/":
        # Calculate seconds until the next hour
        now = datetime.now()
        seconds_until_next_hour = 3600 - (now.minute * 60 + now.second)
        response.headers['Refresh'] = str(seconds_until_next_hour)
    return response

atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    update_weather_data()  # Initial data fetch    

    app.run(host='0.0.0.0', port=80, debug=True)