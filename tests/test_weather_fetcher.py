import pytest
from app.services.weather_fetcher import WeatherFetcher


@pytest.mark.asyncio
async def test_fetch_weather_mock():
    """Test fetching weather data."""
    fetcher = WeatherFetcher()
    
    weather_data = await fetcher.fetch_weather("Moscow,RU")
    
    assert weather_data is not None
    assert weather_data.city == "Moscow"
    assert weather_data.country == "RU"
    assert weather_data.temperature is not None
    assert weather_data.humidity is not None
    assert weather_data.pressure is not None


@pytest.mark.asyncio
async def test_fetch_weather_various_cities():
    """Test weather data for various cities."""
    fetcher = WeatherFetcher()
    
    # OpenWeatherMap uses ISO country codes (GB instead of UK)
    cities = [
        ("London,GB", "London", "GB"),
        ("Paris,FR", "Paris", "FR"),
        ("Tokyo,JP", "Tokyo", "JP"),
    ]
    
    for city_query, expected_city, expected_country in cities:
        weather_data = await fetcher.fetch_weather(city_query)
        
        assert weather_data is not None
        assert weather_data.city == expected_city
        assert weather_data.country == expected_country


@pytest.mark.asyncio
async def test_weather_data_ranges():
    """Test that weather data is within realistic ranges."""
    fetcher = WeatherFetcher()
    
    weather_data = await fetcher.fetch_weather("Moscow,RU")
    
    assert -50 <= weather_data.temperature <= 60  # Realistic temp range
    assert 0 <= weather_data.humidity <= 100
    assert 900 <= weather_data.pressure <= 1100
    assert weather_data.wind_speed is None or 0 <= weather_data.wind_speed <= 100
    assert weather_data.wind_direction is None or 0 <= weather_data.wind_direction <= 360
    assert weather_data.cloudiness is None or 0 <= weather_data.cloudiness <= 100
    assert weather_data.weather_description is not None
    assert weather_data.weather_main is not None


@pytest.mark.asyncio
async def test_fetch_weather_city_without_country():
    """Test fetching weather with city only (no country code)."""
    fetcher = WeatherFetcher()
    
    weather_data = await fetcher.fetch_weather("Berlin")
    
    assert weather_data is not None
    assert weather_data.city == "Berlin"
    # Real API returns actual country code, mock returns "Unknown"
    assert weather_data.country is not None
    assert len(weather_data.country) >= 2  # At least 2 chars (country code or "Unknown")


@pytest.mark.asyncio
async def test_weather_data_has_timestamp():
    """Test that fetched weather data has a timestamp."""
    fetcher = WeatherFetcher()
    
    weather_data = await fetcher.fetch_weather("Sydney,AU")
    
    assert weather_data.data_timestamp is not None


@pytest.mark.asyncio
async def test_weather_data_has_coordinates():
    """Test that weather data includes coordinates."""
    fetcher = WeatherFetcher()
    
    weather_data = await fetcher.fetch_weather("Rome,IT")
    
    assert weather_data.latitude is not None
    assert weather_data.longitude is not None
    assert -90 <= weather_data.latitude <= 90
    assert -180 <= weather_data.longitude <= 180
