

import requests
import requests_cache
import time
from datetime import timedelta

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        # Cache requests for 1 hour
        requests_cache.install_cache('weather_cache', backend='sqlite', expire_after=timedelta(hours=1))

    def get_weather(self, postal_code):
        """Fetches the current weather for a given postal code."""
        return self._make_request(f"{self.base_url}/weather", {'zip': f"{postal_code},gb", 'appid': self.api_key})

    def get_forecast(self, postal_code):
        """Fetches the 5-day forecast for a given postal code."""
        return self._make_request(f"{self.base_url}/forecast", {'zip': f"{postal_code},gb", 'appid': self.api_key})

    def _make_request(self, url, params, retries=3, backoff_factor=0.3):
        """Makes a request to the OpenWeatherMap API with retry logic."""
        for i in range(retries):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raise an exception for bad status codes
                return response.json()
            except requests.exceptions.RequestException as e:
                if i < retries - 1:
                    time.sleep(backoff_factor * (2 ** i)) # Exponential backoff
                    continue
                else:
                    raise e

if __name__ == '__main__':
    # Replace with your actual API key
    API_KEY = "YOUR_API_KEY"
    weather_service = WeatherService(API_KEY)

    postal_code = "SW1A 1AA"

    try:
        current_weather = weather_service.get_weather(postal_code)
        print("Current Weather:")
        print(current_weather)

        forecast = weather_service.get_forecast(postal_code)
        print("\n5-Day Forecast:")
        print(forecast)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

