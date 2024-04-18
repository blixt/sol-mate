import math
import textwrap
from datetime import datetime
from typing import Dict, List

import ephem
import pytz
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from modal import Image, Stub, asgi_app

image = Image.debian_slim().pip_install("ephem", "pytz", "requests")
stub = Stub("sol-mate", image=image)

web_app = FastAPI()

weather_codes = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow fall",
    73: "moderate snow fall",
    75: "heavy snow fall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "slight thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}


def describe_sun_and_moon(
    latitude: float, longitude: float, cloud_cover: float
) -> List[str | None]:
    observer = ephem.Observer()
    observer.lat, observer.lon = str(latitude), str(longitude)
    observer.date = datetime.utcnow()

    sun = ephem.Sun(observer)
    moon = ephem.Moon(observer)

    # Convert celestial bodies' altitude to degrees
    sun_alt_deg = sun.alt * (180.0 / math.pi)

    # Sun status
    sun_status = "It is dark."
    if -18 < sun_alt_deg <= -12:
        sun_status = "It is dark, with hints of twilight."
    elif -12 < sun_alt_deg <= -6:
        sun_status = "It is twilight."
    elif -6 < sun_alt_deg < 0:
        sun_status = "It is the blue hour."
    elif 0 <= sun_alt_deg <= 6:
        sun_status = "It is the golden hour."
    elif sun_alt_deg > 6:
        if cloud_cover >= 0.9:
            sun_status = "The sun is hidden behind clouds."
        elif sun_alt_deg > 20:
            sun_status = "The sun is high in the sky."
        else:
            sun_status = "The sun is low in the sky."

    # Moon status
    moon_status = None
    if sun_alt_deg <= -6:
        moon_phase = observer.date - ephem.previous_new_moon(observer.date)
        moon_alt_deg = moon.alt * (180.0 / math.pi)
        if moon_alt_deg > 0 and cloud_cover >= 0.9:
            if sun_alt_deg < -12:
                moon_status = "The moon is shining through the clouds."
        elif moon_alt_deg > 0:
            if moon_phase < 3 or moon_phase > 25:
                moon_status = "A crescent moon is visible in the sky."
            elif 7 < moon_phase < 22:
                moon_status = "A gibbous moon is visible in the sky."
            elif 13 < moon_phase < 15:
                moon_status = "A full moon is visible in the sky."
            else:
                moon_status = "The moon is visible in the sky."

    return [sun_status, moon_status]


def describe_clouds(cloud_cover: float) -> str:
    if cloud_cover < 0.1:
        return "There's not a single cloud in the sky."
    elif cloud_cover < 0.3:
        return "The sky is mostly clear with a few clouds."
    elif cloud_cover < 0.7:
        return "The sky is partly cloudy."
    elif cloud_cover < 0.9:
        return "The sky is mostly cloudy."
    else:
        return "The sky is completely overcast."


def describe_snow(snow_depth: float) -> str | None:
    if snow_depth == 0:
        return None
    elif snow_depth < 0.01:
        return "There is a light dusting of snow on the ground."
    elif snow_depth < 0.1:
        return "There is snow on the ground."
    else:
        return "There is a thick layer of snow on the ground."


def describe_wind(wind_speed: float) -> str | None:
    if wind_speed < 1:
        return None
    elif wind_speed < 20:
        return "There's a light breeze gently blowing."
    elif wind_speed < 40:
        return "A moderate breeze is blowing."
    elif wind_speed < 60:
        return "There's a strong wind blowing."
    elif wind_speed < 90:
        return "A gale is blowing with very strong winds."
    else:
        return "The wind is stormy and extremely strong."


@web_app.get("/current")
def get_weather(
    latitude: float, longitude: float, timezone: str, temperature_unit: str
) -> Dict[str, str]:
    import requests

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "current": "temperature_2m,snow_depth,weather_code,cloud_cover,wind_speed_10m",
        "temperature_unit": temperature_unit,
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }

    response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
    data = response.json()

    values = data["current"]
    units = data["current_units"]

    cloud_cover = values["cloud_cover"] / 100
    local_time = datetime.now(pytz.timezone(timezone))

    conditions = [
        f'Temperature: {round(values["temperature_2m"])}{units["temperature_2m"]}',
        f'Weather condition: {weather_codes.get(values["weather_code"], "Unknown")}',
        f'The local time is {local_time.strftime("%H:%M")} on a {local_time.strftime("%A in %B")}.',
        *describe_sun_and_moon(latitude, longitude, cloud_cover),
        describe_clouds(cloud_cover),
        describe_wind(values["wind_speed_10m"]),
        describe_snow(values["snow_depth"]),
    ]

    return {"status": "\n".join(filter(None, conditions))}


@web_app.get("/privacy")
def get_privacy_policy():
    html = """
    <h1>Privacy Policy</h1>
    <p>Last updated: November 12, 2023</p>

    <h2>1. Introduction</h2>
    <p>Our API provides weather information based on latitude and longitude coordinates. This Privacy Policy explains what information we collect, how we use it, and your rights.</p>

    <h2>2. Information Collection and Use</h2>
    <p>We only collect latitude and longitude information to provide weather data. We do not collect or store any personal data.</p>

    <h2>3. Data Storage</h2>
    <p>We do not store any data provided by users. All requests are processed in real-time.</p>

    <h2>4. Log Files</h2>
    <p>Log files are maintained for operational purposes, but they are not stored for any extended period.</p>

    <h2>5. Changes to This Privacy Policy</h2>
    <p>We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page.</p>

    <h2>6. Contact Us</h2>
    <p>If you have any questions about this Privacy Policy, please contact us at <a href="mailto:me@blixt.nyc">me@blixt.nyc</a>.</p>
    """
    return HTMLResponse(textwrap.dedent(html))


@stub.function()
@asgi_app()
def weather_api():
    return web_app


@stub.local_entrypoint()
def main():
    import requests

    params = {
        "latitude": 40.7128,
        "longitude": -74.006,
        "timezone": "America/New_York",
        "temperature_unit": "fahrenheit",
    }
    print(f"The weather for {params}:")

    api_url = "https://blixt--sol-mate-weather-api-dev.modal.run/current"
    response = requests.get(api_url, params=params)
    print(response.json()["status"])
