from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/weather_db"
    weather_api_key: str = ""
    weather_api_url: str = "https://api.openweathermap.org/data/2.5/weather"
    weather_update_interval_minutes: int = 30
    default_cities: str = "Astana,Almaty,Shymkent,Karagandy,Kostanay,Kyzylorda,Aktobe,Taraz,Turkestan"
    app_name: str = "Weather Service API"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
