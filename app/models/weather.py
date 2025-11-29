from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from app.database import Base


class Weather(Base):
    """Model for storing weather data."""
    
    __tablename__ = "weather"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Location data
    city = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Weather parameters
    temperature = Column(Float, nullable=False)  # Temperature in Celsius
    feels_like = Column(Float, nullable=True)  # Feels like temperature
    humidity = Column(Float, nullable=False)  # Relative humidity in %
    pressure = Column(Float, nullable=False)  # Atmospheric pressure in hPa
    
    # Additional weather data
    wind_speed = Column(Float, nullable=True)  # Wind speed in m/s
    wind_direction = Column(Integer, nullable=True)  # Wind direction in degrees
    cloudiness = Column(Integer, nullable=True)  # Cloudiness in %
    weather_description = Column(String(200), nullable=True)  # Weather description
    weather_main = Column(String(50), nullable=True)  # Main weather condition
    
    # Visibility
    visibility = Column(Integer, nullable=True)  # Visibility in meters
    
    # Timestamps
    data_timestamp = Column(DateTime, nullable=False)  # When data was recorded by source
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for faster queries
    __table_args__ = (
        Index("ix_weather_city_country", "city", "country"),
        Index("ix_weather_data_timestamp", "data_timestamp"),
    )
    
    def __repr__(self):
        return f"<Weather(city={self.city}, temp={self.temperature}°C, humidity={self.humidity}%)>"

