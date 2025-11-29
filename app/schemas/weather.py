from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class WeatherBase(BaseModel):
    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    temperature: float
    humidity: float = Field(..., ge=0, le=100)
    pressure: float = Field(..., gt=0)


class WeatherCreate(WeatherBase):
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    feels_like: Optional[float] = None
    wind_speed: Optional[float] = Field(None, ge=0)
    wind_direction: Optional[int] = Field(None, ge=0, le=360)
    cloudiness: Optional[int] = Field(None, ge=0, le=100)
    weather_description: Optional[str] = Field(None, max_length=200)
    weather_main: Optional[str] = Field(None, max_length=50)
    visibility: Optional[int] = Field(None, ge=0)
    data_timestamp: Optional[datetime] = None


class WeatherUpdate(BaseModel):
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    humidity: Optional[float] = Field(None, ge=0, le=100)
    pressure: Optional[float] = Field(None, gt=0)
    wind_speed: Optional[float] = Field(None, ge=0)
    wind_direction: Optional[int] = Field(None, ge=0, le=360)
    cloudiness: Optional[int] = Field(None, ge=0, le=100)
    weather_description: Optional[str] = Field(None, max_length=200)
    weather_main: Optional[str] = Field(None, max_length=50)
    visibility: Optional[int] = Field(None, ge=0)
    data_timestamp: Optional[datetime] = None


class WeatherResponse(WeatherBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    feels_like: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[int] = None
    cloudiness: Optional[int] = None
    weather_description: Optional[str] = None
    weather_main: Optional[str] = None
    visibility: Optional[int] = None
    data_timestamp: datetime
    created_at: datetime
    updated_at: datetime


class WeatherListResponse(BaseModel):
    items: List[WeatherResponse]
    total: int
    page: int
    size: int
    pages: int


class CityWeatherRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
