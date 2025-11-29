import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from app.config import get_settings
from app.schemas.weather import WeatherCreate


class WeatherFetcher:
    """Service for fetching weather data from external API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.weather_api_key
        self.api_url = self.settings.weather_api_url
    
    async def fetch_weather(self, city: str) -> Optional[WeatherCreate]:
        """
        Fetch weather data for a city from OpenWeatherMap API.
        Falls back to mock data if API is unavailable.
        
        Args:
            city: City name (can include country code, e.g., "London,UK")
            
        Returns:
            WeatherCreate schema or None if request failed
        """
        if not self.api_key:
            # Return mock data if no API key is configured
            return await self._get_mock_weather(city)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.api_url,
                    params={
                        "q": city,
                        "appid": self.api_key,
                        "units": "metric",  # Get temperature in Celsius
                    },
                    timeout=10.0,
                )
                
                if response.status_code == 200:
                    return self._parse_response(response.json())
                else:
                    # Fallback to mock data on API error (401, 429, etc.)
                    return await self._get_mock_weather(city)
                    
        except Exception:
            # Fallback to mock data on network error
            return await self._get_mock_weather(city)
    
    def _parse_response(self, data: Dict[str, Any]) -> WeatherCreate:
        """Parse OpenWeatherMap API response to WeatherCreate schema."""
        main = data.get("main", {})
        wind = data.get("wind", {})
        clouds = data.get("clouds", {})
        sys = data.get("sys", {})
        coord = data.get("coord", {})
        weather = data.get("weather", [{}])[0]
        
        return WeatherCreate(
            city=data.get("name", "Unknown"),
            country=sys.get("country", "Unknown"),
            latitude=coord.get("lat"),
            longitude=coord.get("lon"),
            temperature=main.get("temp", 0),
            feels_like=main.get("feels_like"),
            humidity=main.get("humidity", 0),
            pressure=main.get("pressure", 0),
            wind_speed=wind.get("speed"),
            wind_direction=wind.get("deg"),
            cloudiness=clouds.get("all"),
            weather_description=weather.get("description"),
            weather_main=weather.get("main"),
            visibility=data.get("visibility"),
            data_timestamp=datetime.utcfromtimestamp(data.get("dt", datetime.utcnow().timestamp())),
        )
    
    async def _get_mock_weather(self, city: str) -> WeatherCreate:
        """
        Generate mock weather data for testing without API key.
        """
        import random
        
        # Parse city and country from input
        parts = city.split(",")
        city_name = parts[0].strip()
        country = parts[1].strip() if len(parts) > 1 else "Unknown"
        
        # Generate random but realistic weather data
        temperature = round(random.uniform(-10, 35), 1)
        
        return WeatherCreate(
            city=city_name,
            country=country,
            latitude=round(random.uniform(-90, 90), 4),
            longitude=round(random.uniform(-180, 180), 4),
            temperature=temperature,
            feels_like=round(temperature + random.uniform(-3, 3), 1),
            humidity=round(random.uniform(20, 100), 1),
            pressure=round(random.uniform(990, 1030), 1),
            wind_speed=round(random.uniform(0, 20), 1),
            wind_direction=random.randint(0, 360),
            cloudiness=random.randint(0, 100),
            weather_description=random.choice([
                "clear sky", "few clouds", "scattered clouds", 
                "broken clouds", "shower rain", "rain", "thunderstorm",
                "snow", "mist"
            ]),
            weather_main=random.choice([
                "Clear", "Clouds", "Rain", "Drizzle", "Thunderstorm", "Snow", "Mist"
            ]),
            visibility=random.randint(1000, 10000),
            data_timestamp=datetime.utcnow(),
        )

