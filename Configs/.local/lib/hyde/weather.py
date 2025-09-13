#!/usr/bin/env python

import os
import sys
import json
from datetime import datetime
import requests

### Constants ###
# WMO Weather interpretation codes (Open-Meteo uses these)
# https://open-meteo.com/en/docs
WMO_WEATHER_CODES = {
    0: "☀️",   # Clear sky
    1: "🌤️",   # Mainly clear
    2: "⛅",   # Partly cloudy
    3: "☁️",   # Overcast
    45: "🌫️",  # Fog
    48: "🌫️",  # Depositing rime fog
    51: "🌧️",  # Light drizzle
    53: "🌧️",  # Moderate drizzle
    55: "🌧️",  # Dense drizzle
    61: "🌧️",  # Slight rain
    63: "🌧️",  # Moderate rain
    65: "🌧️",  # Heavy rain
    80: "🌦️",  # Slight rain showers
    81: "🌦️",  # Moderate rain showers
    82: "🌦️",  # Violent rain showers
    95: "⛈️",   # Thunderstorm
    96: "⛈️",   # Thunderstorm with slight hail
    99: "⛈️",   # Thunderstorm with heavy hail
}

### Functions ###
def load_env_file(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    if line.startswith("export "):
                        line = line[len("export ") :]
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value.strip('"')
    except Exception:
        pass

def get_weather_icon(weather_code):
    return WMO_WEATHER_CODES.get(weather_code, "❓")

def get_description(weather_code):
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return descriptions.get(weather_code, "Unknown")

def get_temperature(current_data):
    if temp_unit == "c":
        return f"{current_data['temperature_2m']}°C"
    else:
        temp_f = current_data['temperature_2m'] * 9/5 + 32
        return f"{temp_f:.1f}°F"

def get_feels_like(current_data):
    temp = current_data['temperature_2m']
    humidity = current_data['relative_humidity_2m']
    
    # Simple approximation: feels warmer when humidity is high
    if humidity > 70:
        feels_like = temp + 2
    else:
        feels_like = temp
        
    if temp_unit == "c":
        return f"{feels_like:.1f}°C"
    else:
        feels_like_f = feels_like * 9/5 + 32
        return f"{feels_like_f:.1f}°F"

def get_wind_speed(current_data):
    if windspeed_unit == "km/h":
        return f"{current_data['wind_speed_10m']} km/h"
    else:
        wind_mph = current_data['wind_speed_10m'] * 0.621371
        return f"{wind_mph:.1f} mph"

### Main Script ###
if __name__ == "__main__":
    # Load environment files first
    load_env_file(os.path.join(os.environ.get("HOME"), ".rlocal", "state", "hyde", "staterc"))
    load_env_file(os.path.join(os.environ.get("HOME"), ".local", "state", "hyde", "config"))

    # Set variables from environment with defaults
    temp_unit = os.getenv("WEATHER_TEMPERATURE_UNIT", "c").lower()
    time_format = os.getenv("WEATHER_TIME_FORMAT", "12h").lower()
    windspeed_unit = os.getenv("WEATHER_WINDSPEED_UNIT", "km/h").lower()
    show_icon = os.getenv("WEATHER_SHOW_ICON", "True").lower() in ("true", "1", "t", "y", "yes")
    show_location = os.getenv("WEATHER_SHOW_LOCATION", "True").lower() in ("true", "1", "t", "y", "yes")
    show_today_details = os.getenv("WEATHER_SHOW_TODAY_DETAILS", "True").lower() in ("true", "1", "t", "y", "yes")
    
    try:
        FORECAST_DAYS = int(os.getenv("WEATHER_FORECAST_DAYS", "3"))
    except ValueError:
        FORECAST_DAYS = 3
        
    get_location = os.getenv("WEATHER_LOCATION", "48.8566,2.3522")
    try:
        lat, lon = map(float, get_location.split(","))
    except Exception:
        lat, lon = 48.8566, 2.3522

    # Validate variables
    if temp_unit not in ("c", "f"):
        temp_unit = "c"
    if time_format not in ("12h", "24h"):
        time_format = "12h"
    if windspeed_unit not in ("km/h", "mph"):
        windspeed_unit = "km/h"
    if FORECAST_DAYS not in range(1, 4):
        FORECAST_DAYS = 3

    # Debug prints (to stderr so they don't interfere with JSON output)
    print("DEBUG: temp_unit:", temp_unit, file=sys.stderr)
    print("DEBUG: time_format:", time_format, file=sys.stderr)
    print("DEBUG: windspeed_unit:", windspeed_unit, file=sys.stderr)
    print("DEBUG: show_icon:", show_icon, file=sys.stderr)
    print("DEBUG: show_location:", show_location, file=sys.stderr)
    print("DEBUG: show_today_details:", show_today_details, file=sys.stderr)
    print("DEBUG: FORECAST_DAYS:", FORECAST_DAYS, file=sys.stderr)
    print("DEBUG: get_location:", get_location, file=sys.stderr)

    # Get weather data
    data = {}
    URL = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,weathercode,wind_speed_10m,relative_humidity_2m"
            f"&daily=weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset"
            f"&timezone=auto"
        )

    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        weather = response.json()
    except Exception as e:
        data["text"] = "❓ Weather Error"
        data["tooltip"] = f"Failed to get weather data: {e}"
        print(json.dumps(data))
        sys.exit(1)

    try:
        current = weather["current"]
        daily = weather["daily"]

        # Text for Waybar
        data["text"] = get_temperature(current)
        if show_icon:
            icon = get_weather_icon(current["weathercode"])
            data["text"] = icon + " " + data["text"]
        if show_location:
            data["text"] += f" | Paris, FR"

        # Tooltip
        data["tooltip"] = f"<b>{get_description(current['weathercode'])} {get_temperature(current)}</b>\n"
        data["tooltip"] += f"Feels like: {get_feels_like(current)}\n"
        data["tooltip"] += f"Wind: {get_wind_speed(current)}\n"
        data["tooltip"] += f"Humidity: {current['relative_humidity_2m']}%\n"
        
        # Add forecast for the next few days
        for i in range(min(FORECAST_DAYS, len(daily["time"]))):
            date = daily["time"][i]
            weather_desc = get_description(daily["weathercode"][i])
            weather_icon = get_weather_icon(daily["weathercode"][i])
            
            if temp_unit == "c":
                max_temp = f"{daily['temperature_2m_max'][i]}°C"
                min_temp = f"{daily['temperature_2m_min'][i]}°C"
            else:
                max_temp = f"{daily['temperature_2m_max'][i] * 9/5 + 32:.1f}°F"
                min_temp = f"{daily['temperature_2m_min'][i] * 9/5 + 32:.1f}°F"
                
            # Format sunrise/sunset times
            sunrise = daily["sunrise"][i].split("T")[1][:5]
            sunset = daily["sunset"][i].split("T")[1][:5]
            
            day_label = "Today" if i == 0 else f"Day {i+1}"
            data["tooltip"] += f"\n<b>{day_label} ({date})</b>\n"
            data["tooltip"] += f"{weather_icon} {weather_desc}\n"
            data["tooltip"] += f"⬆️ {max_temp} ⬇️ {min_temp}\n"
            data["tooltip"] += f"🌅 {sunrise} 🌇 {sunset}\n"

    except Exception as e:
        import traceback
        print(f"ERROR: {traceback.format_exc()}", file=sys.stderr)
        data["text"] = "❓ Processing Error"
        data["tooltip"] = f"Failed to process weather data: {e}"

    print(json.dumps(data))
