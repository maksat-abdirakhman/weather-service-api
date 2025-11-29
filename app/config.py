from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/weather_db"
    
    # Weather API (OpenWeatherMap)
    weather_api_key: str = ""
    weather_api_url: str = "https://api.openweathermap.org/data/2.5/weather"
    
    # Scheduler
    weather_update_interval_minutes: int = 30
    
    # Default cities to track
    default_cities: str = "Astana,Almaty,Shymkent,Karagandy,Kostanay,Kyzylorda,Aktobe,Taraz,Turkestan"
    
    # App settings
    app_name: str = "Weather Service API"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

