from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from app.database import Base


class Weather(Base):
    __tablename__ = "weather"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False, index=True)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    temperature = Column(Float, nullable=False)
    feels_like = Column(Float, nullable=True)
    humidity = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Integer, nullable=True)
    cloudiness = Column(Integer, nullable=True)
    weather_description = Column(String(200), nullable=True)
    weather_main = Column(String(50), nullable=True)
    visibility = Column(Integer, nullable=True)
    data_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("ix_weather_city_country", "city", "country"),
        Index("ix_weather_data_timestamp", "data_timestamp"),
    )
    
    def __repr__(self):
        return f"<Weather(city={self.city}, temp={self.temperature}°C, humidity={self.humidity}%)>"
