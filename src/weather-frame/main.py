import locale
import time
import atexit
from datetime import datetime
from flask import Flask, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler

from weather_service import WeatherService
from display_service import DisplayService
from utils import get_weather_icon

app = Flask(__name__)

# Initialize services
weather_service = WeatherService()
display_service = DisplayService()

def update_weather_and_display():
    """Update weather data and display"""
    if weather_service.update_weather_data():
        # Wait a bit for the web page to update with new data
        time.sleep(2)
        display_service.update_display_async()

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
    weather_data = weather_service.get_cached_data()
    if not weather_data:
        weather_service.update_weather_data()
        weather_data = weather_service.get_cached_data()

    # Format locale-dependent data
    if weather_data and 'current' in weather_data:
        current_time = weather_data['current']['time_obj']
        weather_data['current']['formatted_date'] = current_time.strftime('%A %d %B').capitalize()
        
        if 'daily' in weather_data and 'time_objects' in weather_data['daily']:
            dutch_days = []
            for day_obj in weather_data['daily']['time_objects']:
                day_name = day_obj.strftime('%A')[:2].upper()  # First 2 letters, uppercase
                dutch_days.append(day_name)
            weather_data['daily']['time'] = dutch_days
    
    return render_template("index.html", **weather_data)

@app.route("/refresh")
def refresh():
    """Manual refresh endpoint"""
    update_weather_and_display()
    return "Weather data refreshed"

@app.after_request
def add_refresh_header(response):
    """Add auto-refresh header to index page"""
    if request.path == "/":
        now = datetime.now()
        seconds_until_next_hour = 3600 - (now.minute * 60 + now.second)
        response.headers['Refresh'] = str(seconds_until_next_hour)
    return response

# Register template function
app.jinja_env.globals.update(
    get_weather_icon=get_weather_icon
)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_weather_and_display, trigger="interval", hours=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    update_weather_and_display()  # Initial data fetch
    app.run(host='0.0.0.0', port=8080, debug=True)