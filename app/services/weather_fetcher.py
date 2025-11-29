import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from app.config import get_settings
from app.schemas.weather import WeatherCreate


class WeatherFetcher:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.weather_api_key
        self.api_url = self.settings.weather_api_url
    
    async def fetch_weather(self, city: str) -> Optional[WeatherCreate]:
        if not self.api_key:
            return await self._get_mock_weather(city)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.api_url,
                    params={
                        "q": city,
                        "appid": self.api_key,
                        "units": "metric",
                    },
                    timeout=10.0,
                )
                
                if response.status_code == 200:
                    return self._parse_response(response.json())
                else:
                    return await self._get_mock_weather(city)
                    
        except Exception:
            return await self._get_mock_weather(city)
    
    def _parse_response(self, data: Dict[str, Any]) -> WeatherCreate:
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
        import random
        
        parts = city.split(",")
        city_name = parts[0].strip()
        country = parts[1].strip() if len(parts) > 1 else "Unknown"
        
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
